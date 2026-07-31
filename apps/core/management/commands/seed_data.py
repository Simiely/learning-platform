import glob
import os
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.data import CATEGORIES
from apps.core.models import Category, Item

# 所有分类数据统一在 apps/core/data/ 目录维护（每分类一个文件）。
# image_position 是手动校准的视觉焦点（CSS object-position 格式）。
# 不要用 detect_centers --force 覆盖这些值！
# 修改焦点：直接改 data/ 下对应分类文件，然后 seed_data --force 或 seed_sync。


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

        cat_objs = {}
        for cat_data in CATEGORIES:
            cat = Category.objects.create(
                name=cat_data.name, slug=cat_data.slug,
                icon=cat_data.icon,
                description=cat_data.description,
                sort_order=cat_data.sort_order,
                groups=cat_data.groups,
            )
            cat_objs[cat_data.slug] = cat
            self.stdout.write(f'  Created category: {cat_data.name}')

        for cat_data in CATEGORIES:
            cat = cat_objs[cat_data.slug]
            for idx, item_data in enumerate(cat_data.items):
                item = Item.objects.create(
                    category=cat,
                    code=item_data.code,
                    name=item_data.name,
                    english_name=item_data.english_name,
                    emoji=item_data.emoji,
                    fact=item_data.fact,
                    image_position=item_data.image_position or "50% 50%",
                    image_position_ipad_portrait=item_data.image_position_ipad_portrait or "50% 50%",
                    image_position_ipad_landscape=item_data.image_position_ipad_landscape or "50% 50%",
                    image_position_checked=True,
                    sort_order=idx,
                    group=item_data.group or '',
                )

                # Image — write canonical plain name (no Django `_<suffix>`)
                if item_data.img_file:
                    src = os.path.join(MEDIA_ROOT, 'images', item_data.img_file)
                    if os.path.exists(src):
                        with open(src, 'rb') as f:
                            item.image = _write_media_file(os.path.join('images', item_data.img_file), f.read())
                        item.save(update_fields=['image'])
                # Audio zh / en / fact — same canonical-name treatment
                if item_data.audio_file:
                    for sub, field in (('audio', 'audio'), ('audio_en', 'audio_en'), ('audio_fact', 'audio_fact')):
                        src = os.path.join(MEDIA_ROOT, sub, item_data.audio_file)
                        if os.path.exists(src):
                            with open(src, 'rb') as f:
                                setattr(item, field, _write_media_file(os.path.join(sub, item_data.audio_file), f.read()))
                    item.save(update_fields=["audio", "audio_en", "audio_fact"])
                self.stdout.write(f'    {cat.name}: {item_data.name}')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
