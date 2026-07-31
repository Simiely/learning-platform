"""Core views: index, browse, cards, quiz, and AJAX item API."""

from __future__ import annotations

import json
import random
from typing import Any

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .image_utils import emoji_color
from .models import Category, Item, QuizAttempt
from .services import mark_item_viewed, pinyin_initial, sort_by_pinyin


def _to_emoji_digits(n: int) -> str:
    """把数字转成 emoji 数字（如 77 -> 7️⃣7️⃣）"""
    mapping = {
        '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
        '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣',
    }
    return ''.join(mapping[c] for c in str(n))

def index_view(request: Any) -> Any:
    # annotate 在 SQL 层一次性算好各分类条目数（1 次查询），模板直接渲染 cat.item_count
    categories = Category.objects.annotate(item_count=Count("items")).all()
    return render(request, "index.html", {"categories": categories})

def category_browse_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)

    # 区块模式（互斥双选按钮）：?letters=zh 拼音区块 / ?letters=en 英文区块 / 无 = 默认拼音排序无区块
    letters = request.GET.get("letters")
    letters_en = letters == "en"
    letters_zh = letters == "zh"
    show_letters = letters_zh or letters_en

    if letters_en:
        items = sorted(
            category.items.all(),
            key=lambda it: (it.english_name or "").lower(),
        )
    else:
        items = sort_by_pinyin(category.items.all())

    # Attach colour based on emoji for each item + 字母分隔用的首字母
    # initial 按区块模式统一计算（模板 ifchanged 只用这一个变量，避免条件表达式语法问题）
    for item in items:
        item.color = emoji_color(item.emoji or item.name)
        item.pinyin_initial = pinyin_initial(item.name)
        en = (item.english_name or "").strip()
        item.en_initial = en[0].upper() if en and en[0].isalpha() else "#"
        item.initial = item.en_initial if letters_en else item.pinyin_initial

    items_json = json.dumps([it.to_dict() for it in items])

    # 按 Category.groups 配置统计每个分组数量（动态，不写死）
    groups = category.groups or {}
    group_counts = {key: 0 for key in groups}
    for it in items:
        g = it.group or ""
        if g in group_counts:
            group_counts[g] += 1
    # (key, icon, label_text, count) — label 拆成 emoji 图标 + 纯文字，
    # 避免模板 slice 切坏 ZWJ 组合 emoji，也避免 iPad 宽屏下 emoji 重复显示
    group_info = []
    for key, label in groups.items():
        icon, _, text = label.partition(" ")
        group_info.append((key, icon, text or label, group_counts.get(key, 0)))

    return render(
        request,
        "category_browse.html",
        {
            "category": category,
            "items": items,
            "items_json": items_json,
            "group_info": group_info,  # [(key, "🏠", "家里和农场", 13), ...]
            "letters_zh": letters_zh,
            "letters_en": letters_en,
            "show_letters": show_letters,
            "total": len(items),
            "total_emoji": _to_emoji_digits(len(items)),
        },
    )

def category_cards_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)

    items = sort_by_pinyin(category.items.all())
    items_json = json.dumps([it.to_dict() for it in items])
    return render(
        request,
        "category_cards.html",
        {
            "category": category,
            "items": items,
            "items_json": items_json,
            "total": len(items),
        },
    )

def reset_visited(request: Any, slug: str) -> JsonResponse:
    """Reset visited state for all items in a category.

    Client-side storage is handled via localStorage; this endpoint is a no-op
    on the server but exists so the client can POST without errors.
    """
    return JsonResponse({"status": "ok"})

@require_POST
def mark_viewed(request: Any, item_id: int) -> JsonResponse:
    item = get_object_or_404(Item, id=item_id)
    mark_item_viewed(request.user, item)
    return JsonResponse({"status": "ok"})

# ---- Quiz 常量 ----
QUIZ_MIN_ITEMS = 4      # 至少需要多少个条目才能出题
QUIZ_N_DISTRACTORS = 3  # 每个题目干扰项数量（共 4 个选项）
QUIZ_SIZE = 10          # 每组练习的题目数量（前端 quiz.js 也定义，需保持一致）

def category_quiz_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < QUIZ_MIN_ITEMS:
        return render(
            request,
            "category_quiz.html",
            {"category": category, "error": "Need at least 4 items to create a quiz."},
        )

    # Store previous quiz's used IDs; clear current quiz tracking
    session_key = f"quiz_{slug}"
    current_used = request.session.get(session_key, [])
    if current_used:
        request.session[f"{session_key}_prev"] = list(current_used)
    request.session[session_key] = []
    request.session.modified = True

    return render(
        request,
        "category_quiz.html",
        {"category": category, "item_count": len(items)},
    )

def quiz_question_api(request: Any, slug: str) -> JsonResponse:
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < QUIZ_MIN_ITEMS:
        return JsonResponse({"error": "Not enough items"}, status=400)

    session_key = f"quiz_{slug}"
    used_ids = set(request.session.get(session_key, []))
    prev_ids = set(request.session.get(f"{session_key}_prev", []))

    # 服务端题目数上限：本轮已用满 QUIZ_SIZE 则滚动到下一轮（防御 API 直连绕过前端）
    if len(used_ids) >= QUIZ_SIZE:
        request.session[f"{session_key}_prev"] = list(used_ids)
        used_ids = set()
        request.session[session_key] = []
        request.session.modified = True

    # 正确答案：排除本轮已出过的（used_ids）+ 上轮出过的（prev_ids）
    # → 一轮 10 题正确答案互不重复（各分类条目均 ≥ 15 > 10）
    excluded = used_ids | prev_ids
    available = [i for i in items if i.id not in excluded]
    if len(available) < 1:
        # 上轮排除耗尽：退回只排除本轮已出过的
        available = [i for i in items if i.id not in used_ids]
    if len(available) < 1:
        # 全部条目本轮都用过——重置重新开始
        used_ids = set()
        available = list(items)

    correct = random.choice(available)

    # 干扰项：排除"已作正确答案的"（本轮 used + 上轮 prev）+ 本题 correct，
    # 保证正确答案不会混入其他题的选项里（同一张卡不会既当答案又当干扰项）。
    # 剩余池子无放回取 3 个；条目不足（小分类）时允许干扰项跨题复用，
    # 但始终不与任何正确答案重复。
    dist_excluded = set(used_ids) | prev_ids | {correct.id}
    others = [i for i in items if i.id not in dist_excluded]
    random.shuffle(others)
    distractors = others[:QUIZ_N_DISTRACTORS]
    if len(distractors) < QUIZ_N_DISTRACTORS:
        used_dist = {d.id for d in distractors}
        rest = [i for i in items if i.id != correct.id and i.id not in used_dist]
        random.shuffle(rest)
        distractors += rest[:QUIZ_N_DISTRACTORS - len(distractors)]

    options = [correct] + distractors
    random.shuffle(options)

    # Track this question's correct answer
    used_ids.add(correct.id)
    request.session[session_key] = list(used_ids)

    data = {
        "correct_id": correct.id,
        "correct_name": correct.name,
        "image_url": correct.image.url if correct.image else None,
        "image_position": correct.image_position or "50% 50%",
        "image_position_ipad_portrait": correct.image_position_ipad_portrait or "50% 50%",
        "image_position_ipad_landscape": correct.image_position_ipad_landscape or "50% 50%",
        "emoji": correct.emoji,
        "audio_zh": correct.audio.url if correct.audio else "",
        "audio_en": correct.audio_en.url if correct.audio_en else "",
        "options": [
            {
                "id": i.id,
                "name": i.name,
                "english_name": i.english_name,
                "image_url": i.image.url if i.image else None,
            }
            for i in options
        ],
    }
    return JsonResponse(data)

@require_POST
def quiz_submit_batch(request: Any, slug: str) -> JsonResponse:
    category = get_object_or_404(Category, slug=slug)
    try:
        body = json.loads(request.body)
        # 非 dict 的 JSON body（数组/字符串/数字/null）直接拒绝，避免 500
        if not isinstance(body, dict):
            return JsonResponse({"error": "Invalid data"}, status=400)
        total = body.get("total", 0)
        correct = body.get("correct", 0)
    except (json.JSONDecodeError, AttributeError, TypeError):
        return JsonResponse({"error": "Invalid data"}, status=400)

    if not isinstance(total, int) or not isinstance(correct, int):
        return JsonResponse({"error": "Invalid data"}, status=400)
    if total <= 0 or correct < 0 or correct > total:
        return JsonResponse({"error": "Invalid data"}, status=400)

    if request.user.is_authenticated:
        QuizAttempt.objects.create(
            user=request.user,
            category=category,
            total=total,
            correct=correct,
            quiz_type="image_to_name",
        )

    return JsonResponse({"status": "ok"})
