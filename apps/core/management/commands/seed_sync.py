"""Non-destructive seed sync — creates new items, updates existing ones in-place.

Run after adding new items to any category data file (apps/core/data/).
Never deletes existing items or user progress data.
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.data import CATEGORIES
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
        "Sync all category data (apps/core/data/) into DB without deleting existing data. "
        "Creates new items, updates changed fields in-place. "
        "Safe to run on every deploy."
    )

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for cat_data in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                slug=cat_data.slug,
                defaults={
                    "name": cat_data.name,
                    "icon": cat_data.icon,
                    "description": cat_data.description,
                    "sort_order": cat_data.sort_order,
                    "groups": cat_data.groups,
                },
            )
            # 更新非破坏字段（名称/描述/图标/排序/分组配置可能变化）
            changed = False
            for f, v in (
                ("name", cat_data.name),
                ("icon", cat_data.icon),
                ("description", cat_data.description),
                ("sort_order", cat_data.sort_order),
                ("groups", cat_data.groups),
            ):
                if getattr(cat, f) != v:
                    setattr(cat, f, v)
                    changed = True
            if changed:
                cat.save()

            for idx, a in enumerate(cat_data.items):
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

                # 写媒体文件：新建条目，或已有条目缺图/缺音频时补齐（动物等已有完整媒体的条目不覆盖）
                # 图片与音频分开判断，避免"有音频但缺图"的条目图片永不补齐
                if is_new or not item.image:
                    if a.img_file:
                        src = os.path.join(MEDIA_ROOT, "images", a.img_file)
                        if os.path.exists(src):
                            with open(src, "rb") as f:
                                item.image = _write_media_file(os.path.join("images", a.img_file), f.read())
                            item.save(update_fields=["image"])

                if is_new or not item.audio:
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
                    self.stdout.write(f"  + [{cat_data.slug}] {a.name}")
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {created} created, {updated} updated, 0 deleted"
            )
        )
        sys.exit(0)
