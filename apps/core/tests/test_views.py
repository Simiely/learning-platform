"""视图测试：浏览/卡片/练习 API 基本响应与数据完整性。"""
import json

from django.test import TestCase

from apps.core.data import ANIMALS
from apps.core.models import Category, Item


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
