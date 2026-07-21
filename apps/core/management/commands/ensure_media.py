"""
ensure_media - download the media assets (images / audio / audio_en / audio_fact)
into MEDIA_ROOT at container (or local) startup.

The Docker image intentionally does NOT bundle media files (kept light, and so
assets can be updated independently). Instead, on first boot we fetch a tarball
that contains the `media/` tree and extract it. Re-runs are no-ops once the
canonical files are already present, so container restarts do not re-download.

Source is controlled by the MEDIA_SOURCE_URL env var. It defaults to the GitHub
codeload tarball of this repository's master branch. Point it at any tar.gz that
contains a top-level `media/` directory to use your own asset host (COS / S3 / ...).
"""
import os
import tarfile
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

DEFAULT_SOURCE = (
    "https://codeload.github.com/Simiely/learning-platform/tar.gz/refs/heads/master"
)

# A small file we expect to exist after a successful seed/media download.
# Used as the cheap "already downloaded?" check.
_PROBE = ("images", "lion.jpg")


class Command(BaseCommand):
    help = "Download media assets into MEDIA_ROOT if not already present"

    def _already_present(self):
        from django.conf import settings

        probe = os.path.join(settings.MEDIA_ROOT, *_PROBE)
        return os.path.exists(probe)

    def _download_and_extract(self, url):
        import io

        self.stdout.write(f"  Downloading media from {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "learning-platform/ensure-media"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()

        self.stdout.write(f"  Downloaded {len(data) // 1024} KB, extracting media/ ...")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            # Top-level directory inside the tarball, e.g. "learning-platform-master"
            topdir = None
            for m in tar.getmembers():
                if m.isdir() and m.name.count("/") == 0:
                    topdir = m.name
                    break
            if topdir is None:
                raise RuntimeError("Could not determine top-level directory in tarball")

            prefix = f"{topdir}/media/"
            found = False
            for m in tar.getmembers():
                if not m.name.startswith(prefix) or m.name == prefix:
                    continue
                found = True
                rel = m.name[len(prefix):]
                dest = os.path.join(settings.MEDIA_ROOT, rel)
                if m.isdir():
                    os.makedirs(dest, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                src = tar.extractfile(m)
                if src is None:
                    continue
                with open(dest, "wb") as out:
                    out.write(src.read())
            if not found:
                raise RuntimeError("No 'media/' directory found inside the tarball")

    def handle(self, *args, **options):
        from django.conf import settings

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        if self._already_present():
            self.stdout.write(self.style.WARNING(
                "Media assets already present, skipping download."
            ))
            return

        url = os.environ.get("MEDIA_SOURCE_URL") or DEFAULT_SOURCE
        try:
            self._download_and_extract(url)
        except Exception as exc:  # pragma: no cover - network dependent
            self.stderr.write(self.style.ERROR(
                f"Failed to download media assets: {exc}\n"
                "The app will still start, but images/audio may be missing (404). "
                "Check MEDIA_SOURCE_URL and network connectivity."
            ))
            return

        if self._already_present():
            self.stdout.write(self.style.SUCCESS("Media assets ready."))
        else:
            self.stderr.write(self.style.ERROR(
                "Download finished but probe file is missing. Media may be incomplete."
            ))
