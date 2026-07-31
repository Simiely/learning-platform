"""校验数据一致性：DB 条目、媒体文件、data.py 三者对齐。

检查项：
  1. DB 中每条 Item 的 4 个媒体字段都有对应文件存在
  2. data.py 的每只动物在 DB 中都有对应记录（code 匹配）
  3. 报告缺失/多余，返回非零退出码表示有不一致（便于 CI 使用）
"""
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.data import CATEGORIES
from apps.core.models import Category, Item


class Command(BaseCommand):
    help = "Verify DB items, media files and data.py are aligned."

    def handle(self, *args, **options):
        problems = []

        # 1. DB items 媒体文件完整性（按 data/ 中声明的文件校验；img_file 为空 = 用 emoji 代替图片，合法）
        media_root = str(settings.MEDIA_ROOT)
        data_media = {
            a.code: (a.img_file, a.audio_file)
            for cat in CATEGORIES for a in cat.items
        }
        for item in Item.objects.all().select_related("category"):
            img_file, audio_file = data_media.get(item.code, ("", ""))
            # 图片：仅当 data 声明了 img_file 时才要求 image 字段 + 文件存在
            if img_file:
                f = item.image
                if not f:
                    problems.append(f"[{item.code}] 缺少 image 字段（data 声明了 {img_file}）")
                else:
                    path = f.path if hasattr(f, "path") else os.path.join(media_root, "images", os.path.basename(str(f)))
                    if not os.path.exists(path):
                        problems.append(f"[{item.code}] 图片文件不存在: {path}")
            # 音频：data 声明了 audio_file 时必须三个音频字段齐全
            if audio_file:
                for field, sub in (
                    ("audio", "audio"),
                    ("audio_en", "audio_en"),
                    ("audio_fact", "audio_fact"),
                ):
                    f = getattr(item, field)
                    if not f:
                        problems.append(f"[{item.code}] 缺少 {field} 字段")
                        continue
                    path = f.path if hasattr(f, "path") else os.path.join(media_root, sub, os.path.basename(str(f)))
                    if not os.path.exists(path):
                        problems.append(f"[{item.code}] 文件不存在: {path}")

        # 2. data/ 与 DB 对齐（所有分类）
        db_codes = {i.code for i in Item.objects.all()}
        data_codes = {a.code for cat in CATEGORIES for a in cat.items}
        missing_in_db = data_codes - db_codes
        extra_in_db = db_codes - data_codes
        for code in sorted(missing_in_db):
            problems.append(f"data 有但 DB 缺: {code}")
        for code in sorted(extra_in_db):
            problems.append(f"DB 有但 data 无: {code}")

        # 3. Category 检查（data/ 中注册的分类都应在 DB 存在）
        for cat_data in CATEGORIES:
            cat = Category.objects.filter(slug=cat_data.slug).first()
            if not cat:
                problems.append(f"缺少 {cat_data.slug} 分类")
            elif not cat.groups:
                problems.append(f"{cat_data.slug} 分类缺少 groups 配置")

        if problems:
            for p in problems:
                self.stderr.write(self.style.ERROR(f"  ✗ {p}"))
            self.stderr.write(self.style.ERROR(f"\n共 {len(problems)} 个问题"))
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS(
                f"OK: {Item.objects.count()} items, 媒体文件齐全, data/ 与 DB 对齐（{len(CATEGORIES)} 个分类）"
            )
        )
