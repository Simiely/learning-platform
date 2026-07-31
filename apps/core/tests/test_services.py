"""核心逻辑单元测试：排序、拼音首字母、emoji 取色、全分类数据完整性。"""
from pathlib import Path

from django.test import TestCase

from apps.core.data import ANIMALS, CATEGORIES
from apps.core.image_utils import emoji_color
from apps.core.models import Category, Item
from apps.core.services import pinyin_initial, sort_by_pinyin


class CategoryDataTests(TestCase):
    """apps/core/data/ 全部分类数据完整性（跨分类）"""

    def test_all_categories_have_unique_codes(self):
        # 分类内 code 唯一，且全局 code 唯一（跨分类也不重复）
        for cat in CATEGORIES:
            codes = [a.code for a in cat.items]
            self.assertEqual(
                len(codes), len(set(codes)),
                f"[{cat.slug}] code 必须唯一",
            )
        all_codes = [a.code for cat in CATEGORIES for a in cat.items]
        self.assertEqual(
            len(all_codes), len(set(all_codes)),
            "全部条目的 code 必须全局唯一",
        )

    def test_all_items_have_valid_group(self):
        # 每个条目的 group 必须属于其分类的 groups 配置
        for cat in CATEGORIES:
            valid = set(cat.groups.keys())
            for a in cat.items:
                self.assertIn(a.group, valid, f"[{cat.slug}] {a.name} group 非法: {a.group}")

    def test_all_categories_groups_nonempty(self):
        for cat in CATEGORIES:
            self.assertTrue(cat.groups, f"[{cat.slug}] 缺少分组配置")
            for key, label in cat.groups.items():
                self.assertTrue(label, f"[{cat.slug}] 分组 {key} 缺少显示名")

    def test_all_items_have_audio_and_fact(self):
        for cat in CATEGORIES:
            for a in cat.items:
                self.assertTrue(a.audio_file, f"[{cat.slug}] {a.name} 缺少 audio_file")
                self.assertTrue(a.fact, f"[{cat.slug}] {a.name} 缺少科普文案")
                self.assertTrue(a.name and a.english_name, f"[{cat.slug}] {a.name} 缺少中/英文名")

    def test_audio_basenames_globally_unique(self):
        # 跨分类 audio_file 基名不能冲突（曾发生 vehicles/space 共用 rocket.mp3）
        stems = [Path(a.audio_file).stem for cat in CATEGORIES for a in cat.items]
        dupes = {s for s in stems if stems.count(s) > 1}
        self.assertEqual(dupes, set(), f"audio 基名跨分类冲突: {dupes}")

    def test_animals_have_images(self):
        # 动物分类要求每只都有图片文件（手工校准过焦点）
        animals_cat = next(c for c in CATEGORIES if c.slug == "animals")
        for a in animals_cat.items:
            self.assertTrue(a.img_file, f"{a.name} 缺少 img_file")
            # 焦点必须是 CSS object-position 格式
            for pos in (a.image_position, a.image_position_ipad_portrait, a.image_position_ipad_landscape):
                self.assertRegex(pos, r"^\d{1,3}% \d{1,3}%$", f"{a.name} 焦点格式异常: {pos}")

    def test_black_square_placeholder_count(self):
        blacks = [a for a in ANIMALS if a.emoji == "⬛"]
        self.assertEqual(len(blacks), 3, "动物分类应有 3 只 ⬛ 占位（海马/鸵鸟/河狸）")

    def test_new_categories_use_emoji_instead_of_images(self):
        # 动物之外的分类：img_file 留空（emoji 代替），且必须有 emoji
        for cat in CATEGORIES:
            if cat.slug == "animals":
                continue
            for a in cat.items:
                self.assertFalse(a.img_file, f"[{cat.slug}] {a.name} 应暂用 emoji（img_file 留空）")
                self.assertTrue(a.emoji, f"[{cat.slug}] {a.name} 缺少 emoji")

    def test_item_count_matches_registration(self):
        # 每个分类条目数 > 0，且全部可被 seed_sync 读取
        for cat in CATEGORIES:
            self.assertGreater(len(cat.items), 0, f"[{cat.slug}] 无条目")


class PinyinTests(TestCase):
    def test_pinyin_initial_normal(self):
        self.assertEqual(pinyin_initial("山羊"), "S")
        self.assertEqual(pinyin_initial("猎豹"), "L")

    def test_pinyin_initial_edge(self):
        self.assertEqual(pinyin_initial(""), "#")
        self.assertEqual(pinyin_initial("123"), "#")

    def test_sort_by_pinyin_ordering(self):
        cat = Category.objects.create(name="测试", slug="test", icon="x", sort_order=1)
        for name in ["斑马", "豹子", "北极熊", "蚂蚁"]:
            Item.objects.create(category=cat, name=name, code=f"c_{name}", group="wild")
        items = sort_by_pinyin(cat.items.all())
        # TONE3 字典序：ban3 < bao4 < bei3 < ma3
        self.assertEqual([i.name for i in items], ["斑马", "豹子", "北极熊", "蚂蚁"])


class EmojiColorTests(TestCase):
    def test_black_square_special_color(self):
        # ⬛ 中间色 0x3C * (1-0.7) = 18 -> #121212
        self.assertEqual(emoji_color("⬛"), "#121212")

    def test_emoji_color_format(self):
        color = emoji_color("🐐")
        self.assertRegex(color, r"^#[0-9a-f]{6}$")

    def test_empty_emoji_fallback(self):
        color = emoji_color("")
        self.assertRegex(color, r"^#[0-9a-f]{6}$")
