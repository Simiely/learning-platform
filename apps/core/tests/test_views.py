"""视图测试：浏览/卡片/练习 API 基本响应与数据完整性（含多分类）。"""
import json
import re

from django.test import TestCase

from apps.core.data import ANIMALS, CATEGORIES
from apps.core.models import Category, Item


def _seed_category(cat_data, limit=None):
    """按数据定义创建分类 + 条目（可只取前 N 条），返回 Category。"""
    cat, _ = Category.objects.get_or_create(
        slug=cat_data.slug,
        defaults={
            "name": cat_data.name, "icon": cat_data.icon,
            "description": cat_data.description,
            "sort_order": cat_data.sort_order, "groups": cat_data.groups,
        },
    )
    items = cat_data.items[:limit] if limit else cat_data.items
    for idx, a in enumerate(items):
        Item.objects.get_or_create(
            category=cat, code=a.code,
            defaults={
                "name": a.name, "english_name": a.english_name, "emoji": a.emoji,
                "fact": a.fact, "group": a.group, "sort_order": idx,
                "image_position_checked": True,
            },
        )
    return cat


class BrowseViewTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="动物", slug="animals", icon="🐾", sort_order=1)
        for idx, a in enumerate(ANIMALS[:10]):
            Item.objects.create(
                category=self.cat, code=a.code, name=a.name,
                english_name=a.english_name, emoji=a.emoji, fact=a.fact,
                group=a.group, sort_order=idx, image_position_checked=True,
            )

    def test_index_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_browse_page_renders_all_tiles(self):
        resp = self.client.get("/category/animals/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("browse-grid", html)
        self.assertIn("browseApp", html)  # 独立 JS 初始化
        for a in ANIMALS[:10]:
            self.assertIn(a.name, html)

    def test_browse_letters_en_orders_by_english(self):
        # ?letters=en 按英文名排序 + 初始开启英文区块（lettersEnabled: true、🔤 选中）
        resp = self.client.get("/category/animals/?letters=en")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("lettersEnabled: true", html, "英文区块应初始开启")
        self.assertIn("toggleLetterMode('en')", html)
        self.assertIn("letter-toggle active", html, "🔤 应为选中状态")
        m = re.search(r"items: (\[.*?\]),\s*lettersEnabled", html, re.S)
        self.assertTrue(m, "应能提取 items_json")
        items = json.loads(m.group(1))
        names = [it["english_name"] for it in items]
        self.assertEqual(
            names, sorted(names, key=lambda s: (s or "").lower()),
            "英文区块应按英文名排序",
        )

    def test_browse_default_has_no_letter_dividers(self):
        # 默认（无参数）：拼音排序、无字母区块、两按钮都未选中
        resp = self.client.get("/category/animals/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("lettersEnabled: false", html, "默认不应开启区块")
        self.assertNotIn("b-letter-divider", html, "默认不应渲染字母分块")
        self.assertIn("toggleLetterMode('zh')", html)
        self.assertIn("toggleLetterMode('en')", html)

    def test_letter_dividers_grouped_by_initial(self):
        # 区块模式下，同首字母的条目只渲染一个字母分块（区域块正确合并，不逐条重复）
        for url in ("/category/animals/?letters=zh", "/category/animals/?letters=en"):
            resp = self.client.get(url)
            html = resp.content.decode()
            letters = re.findall(r'ld-badge">([A-Z#])</span>', html)
            merged = sum(
                1 for i, l in enumerate(letters) if i == 0 or l != letters[i - 1]
            )
            self.assertEqual(
                len(letters), merged, f"{url} 相邻同字母应合并为一个分块",
            )
            self.assertEqual(
                len(letters), len(set(letters)), f"{url} 分块应按字母分组",
            )

    def test_cards_page_renders(self):
        resp = self.client.get("/category/animals/cards/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cardsApp", resp.content.decode())

    def test_quiz_page_renders(self):
        resp = self.client.get("/category/animals/quiz/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("quizApp", resp.content.decode())

    def test_quiz_question_api(self):
        resp = self.client.get("/api/quiz/animals/question/?type=image_to_name")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn("correct_id", data)
        self.assertEqual(len(data["options"]), 4, "应有 4 个选项")

    def test_mark_viewed_requires_post(self):
        item = Item.objects.first()
        resp = self.client.get(f"/api/mark-viewed/{item.id}/")
        self.assertEqual(resp.status_code, 405, "GET 应被拒绝")

    def test_reset_visited(self):
        resp = self.client.post("/api/reset-visited/animals/")
        self.assertEqual(resp.status_code, 200)


class QuizSubmitTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="动物", slug="animals", icon="🐾", sort_order=1)
        for idx, a in enumerate(ANIMALS[:4]):
            Item.objects.create(
                category=self.cat, code=a.code, name=a.name,
                english_name=a.english_name, emoji=a.emoji, fact=a.fact,
                group=a.group, sort_order=idx, image_position_checked=True,
            )

    def test_submit_valid(self):
        resp = self.client.post(
            "/api/quiz/animals/submit/",
            data=json.dumps({"total": 10, "correct": 8, "quiz_type": "image_to_name"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_submit_invalid_range(self):
        resp = self.client.post(
            "/api/quiz/animals/submit/",
            data=json.dumps({"total": 10, "correct": 12}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_rejects_non_dict_body(self):
        # 非 dict JSON body 应返回 400，而不是 500
        for payload in ([1, 2, 3], "abc", None, 123, "null"):
            resp = self.client.post(
                "/api/quiz/animals/submit/",
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 400, f"payload={payload!r} 应 400")


class MultiCategoryViewTests(TestCase):
    """全部 7 个分类的视图/API 回归测试（多分类扩展保护）。"""

    def setUp(self):
        for cat_data in CATEGORIES:
            _seed_category(cat_data)

    def test_all_categories_browse_pages(self):
        for cat in CATEGORIES:
            with self.subTest(slug=cat.slug):
                resp = self.client.get(f"/category/{cat.slug}/")
                self.assertEqual(resp.status_code, 200)
                html = resp.content.decode()
                self.assertIn("browse-grid", html)
                # 分组按钮来自 Category.groups 配置
                for key in cat.groups:
                    self.assertIn(f'data-group="{key}"', html, f"[{cat.slug}] 缺分组按钮 {key}")
                # 冗余 data-item-* 属性已清理（数据统一走 items_json 数组）
                self.assertNotIn("data-item-name", html, f"[{cat.slug}] 冗余属性未清理")

    def test_all_categories_cards_pages(self):
        for cat in CATEGORIES:
            with self.subTest(slug=cat.slug):
                resp = self.client.get(f"/category/{cat.slug}/cards/")
                self.assertEqual(resp.status_code, 200)
                self.assertIn("cardsApp", resp.content.decode())

    def test_all_categories_quiz_pages(self):
        for cat in CATEGORIES:
            with self.subTest(slug=cat.slug):
                resp = self.client.get(f"/category/{cat.slug}/quiz/")
                self.assertEqual(resp.status_code, 200)
                self.assertIn("quizApp", resp.content.decode())

    def test_all_categories_quiz_api(self):
        for cat in CATEGORIES:
            if len(cat.items) < 4:
                continue
            with self.subTest(slug=cat.slug):
                resp = self.client.get(f"/api/quiz/{cat.slug}/question/?type=image_to_name")
                self.assertEqual(resp.status_code, 200)
                data = json.loads(resp.content)
                self.assertIn("correct_id", data)
                self.assertEqual(len(data["options"]), 4, "应有 4 个选项")

    def test_all_categories_reset_visited(self):
        for cat in CATEGORIES:
            with self.subTest(slug=cat.slug):
                resp = self.client.post(f"/api/reset-visited/{cat.slug}/")
                self.assertEqual(resp.status_code, 200)

    def test_index_shows_all_categories(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        for cat in CATEGORIES:
            self.assertIn(cat.name, html, f"首页缺分类 {cat.name}")
            # annotate 的条目数正确渲染（模板 cat.item_count 应为 int）
            self.assertIn(f"{len(cat.items)} 张", html, f"[{cat.slug}] 首页条目数不对")


class QuizNoRepeatTests(TestCase):
    """一轮练习（10 题）内不重复：正确答案互不重复，且正确答案不会混入其他题选项。"""

    QUIZ_N = 10

    def setUp(self):
        # 20 条（模拟条目较少的新分类场景，10 题 × 4 选项 > 条目数的物理限制下仍须保证答案不重复）
        self.cat = Category.objects.create(
            name="动物", slug="animals", icon="🐾", sort_order=1,
            groups={"farm": "🏠 家里和农场", "wild": "🌍 野生动物"},
        )
        for idx, a in enumerate(ANIMALS[:20]):
            Item.objects.create(
                category=self.cat, code=a.code, name=a.name,
                english_name=a.english_name, emoji=a.emoji, fact=a.fact,
                group="wild", sort_order=idx, image_position_checked=True,
            )

    def _fetch_questions(self, n):
        questions = []
        for _ in range(n):
            resp = self.client.get("/api/quiz/animals/question/")
            self.assertEqual(resp.status_code, 200)
            questions.append(json.loads(resp.content))
        return questions

    def test_correct_answers_no_repeat(self):
        # 核心：10 道题的正确答案互不重复（不重复考同一张卡）
        questions = self._fetch_questions(self.QUIZ_N)
        correct_ids = [q["correct_id"] for q in questions]
        self.assertEqual(
            len(correct_ids), len(set(correct_ids)),
            f"一轮 {self.QUIZ_N} 题正确答案不应重复",
        )

    def test_options_are_unique_per_question(self):
        for i, q in enumerate(self._fetch_questions(self.QUIZ_N)):
            opts = [o["id"] for o in q["options"]]
            self.assertEqual(len(opts), 4, f"第 {i+1} 题应有 4 个选项")
            self.assertEqual(len(set(opts)), 4, f"第 {i+1} 题选项不应重复")

    def test_past_correct_not_reused_later(self):
        # 已出过的正确答案，不会再出现在后续题目的选项里（时间正向去重）
        questions = self._fetch_questions(self.QUIZ_N)
        seen_correct = set()
        for i, q in enumerate(questions):
            opts = [o["id"] for o in q["options"]]
            overlap = seen_correct & set(opts)
            self.assertEqual(overlap, set(), f"第 {i+1} 题选项含已出过的答案: {overlap}")
            seen_correct.add(q["correct_id"])
