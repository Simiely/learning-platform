"""核心逻辑单元测试：排序、拼音首字母、emoji 取色、数据完整性。"""
from django.test import TestCase

from apps.core.data import ANIMALS
from apps.core.image_utils import emoji_color
from apps.core.models import Category, Item
from apps.core.services import pinyin_initial, sort_by_pinyin


class AnimalDataTests(TestCase):
    """apps/core/data.py 数据完整性"""

    def test_all_animals_have_unique_codes(self):
        codes = [a.code for a in ANIMALS]
        self.assertEqual(len(codes), len(set(codes)), "code 必须唯一")

    def test_all_animals_have_valid_group(self):
        valid = {"farm", "wild", "ocean", "reptile"}
        for a in ANIMALS:
            self.assertIn(a.group, valid, f"{a.name} group 非法: {a.group}")

    def test_all_animals_have_media_filenames(self):
        for a in ANIMALS:
            self.assertTrue(a.img_file, f"{a.name} 缺少 img_file")
            self.assertTrue(a.audio_file, f"{a.name} 缺少 audio_file")

    def test_all_animals_have_fact(self):
        for a in ANIMALS:
            self.assertTrue(a.fact, f"{a.name} 缺少科普文案")

    def test_black_square_placeholder_count(self):
        blacks = [a for a in ANIMALS if a.emoji == "⬛"]
        self.assertEqual(len(blacks), 3, "应有 3 只 ⬛ 占位（海马/鸵鸟/河狸）")


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
