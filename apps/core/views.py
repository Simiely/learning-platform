"""Core views: index, browse, cards, quiz, and AJAX item API."""

from __future__ import annotations

import json
import random
from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .image_utils import _emoji_color, _detect_image_center, _hash_tile_color
from .models import Category, Item, LearningProgress, QuizAttempt


def index_view(request: Any) -> Any:
    categories = Category.objects.prefetch_related("items").all()
    return render(request, "index.html", {"categories": categories})


def category_browse_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)
    from pypinyin import Style, pinyin

    items = sorted(
        list(category.items.all()),
        key=lambda it: pinyin(it.name, style=Style.TONE3)[0][0] if it.name else "",
    )

    # Attach colour based on emoji for each item
    for item in items:
        item.color = _emoji_color(item.emoji or item.name)

    items_json = json.dumps([it.to_dict() for it in items])

    return render(
        request,
        "category_browse.html",
        {"category": category, "items": items, "items_json": items_json},
    )


def category_cards_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)
    from pypinyin import Style, pinyin

    items = sorted(
        list(category.items.all()),
        key=lambda it: pinyin(it.name, style=Style.TONE3)[0][0] if it.name else "",
    )
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


def item_detail_api(request: Any, item_id: int) -> JsonResponse:
    item = get_object_or_404(Item, id=item_id)
    if request.user.is_authenticated:
        progress, created = LearningProgress.objects.get_or_create(
            user=request.user,
            item=item,
            defaults={"learned": True, "view_count": 1},
        )
        if not created:
            progress.view_count = models.F("view_count") + 1
            progress.learned = True
            progress.save(update_fields=["view_count", "learned"])
    return JsonResponse(item.to_dict())


def reset_visited(request: Any, slug: str) -> JsonResponse:
    """Reset visited state for all items in a category.

    Client-side storage is handled via localStorage; this endpoint is a no-op
    on the server but exists so the client can POST without errors.
    """
    return JsonResponse({"status": "ok"})


def mark_viewed(request: Any, item_id: int) -> JsonResponse:
    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id)
        if request.user.is_authenticated:
            progress, created = LearningProgress.objects.get_or_create(
                user=request.user,
                item=item,
                defaults={"learned": True, "view_count": 1},
            )
        if not created:
            progress.view_count = F("view_count") + 1
            progress.learned = True
            progress.save(update_fields=["view_count", "learned"])
            return JsonResponse({"status": "ok", "view_count": progress.view_count})
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


def category_quiz_view(request: Any, slug: str) -> Any:
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < 4:
        return render(
            request,
            "category_quiz.html",
            {"category": category, "error": "Need at least 4 items to create a quiz."},
        )

    quiz_type = request.GET.get("type", request.session.get("quiz_type", "image_to_name"))
    request.session["quiz_type"] = quiz_type

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
        {"category": category, "quiz_type": quiz_type, "item_count": len(items)},
    )


def quiz_question_api(request: Any, slug: str) -> JsonResponse:
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < 4:
        return JsonResponse({"error": "Not enough items"}, status=400)

    quiz_type = request.GET.get("type", "image_to_name")
    session_key = f"quiz_{slug}"
    used_ids = set(request.session.get(session_key, []))
    prev_ids = set(request.session.get(f"{session_key}_prev", []))

    # Exclude already-used (current session) and previous session IDs
    excluded = used_ids | prev_ids
    available = [i for i in items if i.id not in excluded]
    # If not enough unique items left, just exclude current session duplicates
    if len(available) < 1:
        available = [i for i in items if i.id not in used_ids]
    if len(available) < 1:
        # All items used at least once — reset and start fresh
        used_ids = set()
        available = list(items)

    correct = random.choice(available)
    # Distractors: prefer items not yet used this session or last session
    others = [i for i in items if i.id != correct.id]
    # Shuffle to avoid same distractors every time
    random.shuffle(others)
    distractors = others[:3]

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
        "emoji": correct.emoji,
        "audio_zh": correct.audio.url if correct.audio else "",
        "audio_en": correct.audio_en.url if correct.audio_en else "",
        "quiz_type": quiz_type,
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
        total = body.get("total", 0)
        correct = body.get("correct", 0)
        quiz_type = body.get("quiz_type", "image_to_name")
    except (json.JSONDecodeError, KeyError):
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
            quiz_type=quiz_type,
        )

    return JsonResponse({"status": "ok"})
