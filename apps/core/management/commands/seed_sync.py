"""Non-destructive seed sync — creates new animals, updates existing ones in-place.

Run after adding new animals to apps/core/data.py ANIMALS list.
Never deletes existing items or user progress data.
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.data import ANIMALS
from apps.core.models import Category, Item

MEDIA_ROOT = str(getattr(settings, "MEDIA_ROOT", ""))


def _write_media_file(rel_path, content):
    """Write a file relative to MEDIA_ROOT, returning None on failure."""
    if not MEDIA_ROOT:
        return None
    full = os.path.join(MEDIA_ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(content)
    return rel_path


class Command(BaseCommand):
    help = (
        "Sync seed_data ANIMALS into DB without deleting existing data. "
        "Creates new items, updates changed fields in-place. "
        "Safe to run on every deploy."
    )

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(
            slug="animals",
            defaults={"name": "动物", "icon": "🐾", "sort_order": 0},
        )

        created = 0
        updated = 0

        for idx, a in enumerate(ANIMALS):
            defaults = {
                "name": a.name,
                "english_name": a.english_name,
                "emoji": a.emoji,
                "fact": a.fact,
                "image_position": a.image_position or "50% 50%",
                "image_position_ipad_portrait": a.image_position_ipad_portrait or "50% 50%",
                "image_position_ipad_landscape": a.image_position_ipad_landscape or "50% 50%",
                "group": a.group,
                "sort_order": idx,
                "image_position_checked": True,
            }

            item, is_new = Item.objects.update_or_create(
                category=cat, code=a.code, defaults=defaults
            )

            # Only write media files for NEW items to avoid unnecessary overwrites
            if is_new and a.img_file:
                src = os.path.join(MEDIA_ROOT, "images", a.img_file)
                if os.path.exists(src):
                    with open(src, "rb") as f:
                        item.image = _write_media_file(os.path.join("images", a.img_file), f.read())
                    item.save(update_fields=["image"])

                if a.audio_file:
                    for sub, field in (
                        ("audio", "audio"),
                        ("audio_en", "audio_en"),
                        ("audio_fact", "audio_fact"),
                    ):
                        src = os.path.join(MEDIA_ROOT, sub, a.audio_file)
                        if os.path.exists(src):
                            with open(src, "rb") as f:
                                setattr(
                                    item,
                                    field,
                                    _write_media_file(os.path.join(sub, a.audio_file), f.read()),
                                )
                    item.save(update_fields=["audio", "audio_en", "audio_fact"])

            if is_new:
                created += 1
                self.stdout.write(f"  + {a.name}")
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {created} created, {updated} updated, 0 deleted"
            )
        )
        sys.exit(0)
