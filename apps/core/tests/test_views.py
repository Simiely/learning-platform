"""视图测试：浏览/卡片/练习 API 基本响应与数据完整性（含多分类）。"""
import json

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
