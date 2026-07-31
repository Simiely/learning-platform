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

from apps.core.data import ANIMALS
from apps.core.models import Category, Item


class Command(BaseCommand):
    help = "Verify DB items, media files and data.py are aligned."

    def handle(self, *args, **options):
        problems = []

        # 1. DB items 媒体文件完整性
        media_root = str(settings.MEDIA_ROOT)
        for item in Item.objects.all().select_related("category"):
            for field, sub in (
                ("image", "images"),
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

        # 2. data.py 与 DB 对齐
        db_codes = {i.code for i in Item.objects.all()}
        data_codes = {a.code for a in ANIMALS}
        missing_in_db = data_codes - db_codes
        extra_in_db = db_codes - data_codes
        for code in sorted(missing_in_db):
            problems.append(f"data.py 有但 DB 缺: {code}")
        for code in sorted(extra_in_db):
            problems.append(f"DB 有但 data.py 无: {code}")

        # 3. Category 检查
        if not Category.objects.filter(slug="animals").exists():
            problems.append("缺少 animals 分类")

        if problems:
            for p in problems:
                self.stderr.write(self.style.ERROR(f"  ✗ {p}"))
            self.stderr.write(self.style.ERROR(f"\n共 {len(problems)} 个问题"))
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS(
                f"OK: {Item.objects.count()} items, 媒体文件齐全, data.py 与 DB 对齐"
            )
        )
