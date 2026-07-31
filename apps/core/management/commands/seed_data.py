import glob
import os
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.data import ANIMALS
from apps.core.models import Category, Item

# 动物数据统一在 apps/core/data.py 维护（dataclass Animal）。
# image_position 是手动校准的视觉焦点（CSS object-position 格式）。
# 不要用 detect_centers --force 覆盖这些值！
# 修改焦点：直接改 data.py，然后 seed_data --force 或 seed_sync。


def _write_media_file(rel_path, content_bytes):
    """Write bytes to MEDIA_ROOT/rel_path deterministically.

    Django's FileField.save() appends a random `_<suffix>` when the target
    name already exists on disk (e.g. re-running seed_data over the committed
    media files). That desyncs the DB filename from the canonical file and
    causes 404s. This helper overwrites the canonical plain name instead and
    removes any leftover suffixed orphans, so the stored name always equals
    rel_path and survives a fresh clone + migrate + seed_data anywhere.
    """
    from django.conf import settings
    base_dir, fname = os.path.split(rel_path)
    stem, dot, ext = fname.rpartition(".")
    full_dir = os.path.join(settings.MEDIA_ROOT, base_dir)
    os.makedirs(full_dir, exist_ok=True)
    if stem and ext:
        for old in glob.glob(os.path.join(full_dir, f'{stem}_*.{ext}')):
            try:
                os.remove(old)
            except OSError:
                pass
    dest = os.path.join(full_dir, fname)
    with open(dest, 'wb') as fh:
        fh.write(content_bytes)
    return rel_path.replace('\\', '/')


class Command(BaseCommand):
    help = "Seed the database with sample categories and items"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing data without confirmation",
        )

    def handle(self, *args, **options):
        MEDIA_ROOT = settings.MEDIA_ROOT

        if Category.objects.exists() and not options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "Data already exists. Use --force to overwrite, "
                    "or delete existing data first."
                )
            )
            return

        Item.objects.all().delete()
        Category.objects.all().delete()

        categories_data = [
            ('动物', 'animals', '认识各种动物', 1, '🐾'),
        ]

        cat_objs = {}
        for name, slug, desc, order, icon in categories_data:
            cat = Category.objects.create(
                name=name, slug=slug,
                icon=icon,
                description=desc, sort_order=order
            )
            cat_objs[slug] = cat
            self.stdout.write(f'  Created category: {name}')

        items_data = [
            ('animals', ANIMALS, True),
        ]

        for slug, items, use_real_media in items_data:
            cat = cat_objs[slug]
            for idx, animal in enumerate(items):
                item = Item.objects.create(
                    category=cat,
                    code=animal.code,
                    name=animal.name,
                    english_name=animal.english_name,
                    emoji=animal.emoji,
                    fact=animal.fact,
                    image_position=animal.image_position or "50% 50%",
                    image_position_ipad_portrait=animal.image_position_ipad_portrait or "50% 50%",
                    image_position_ipad_landscape=animal.image_position_ipad_landscape or "50% 50%",
                    image_position_checked=True,
                    sort_order=idx,
                    group=animal.group or '',
                )

                if use_real_media:
                    # Image — write canonical plain name (no Django `_<suffix>`)
                    if animal.img_file:
                        src = os.path.join(MEDIA_ROOT, 'images', animal.img_file)
                        if os.path.exists(src):
                            with open(src, 'rb') as f:
                                item.image = _write_media_file(os.path.join('images', animal.img_file), f.read())
                            item.save(update_fields=['image'])
                    # Audio zh / en / fact — same canonical-name treatment
                    if animal.audio_file:
                        for sub, field in (('audio', 'audio'), ('audio_en', 'audio_en'), ('audio_fact', 'audio_fact')):
                            src = os.path.join(MEDIA_ROOT, sub, animal.audio_file)
                            if os.path.exists(src):
                                with open(src, 'rb') as f:
                                    setattr(item, field, _write_media_file(os.path.join(sub, animal.audio_file), f.read()))
                        item.save(update_fields=["audio", "audio_en", "audio_fact"])
                self.stdout.write(f'    {cat.name}: {animal.name}')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
