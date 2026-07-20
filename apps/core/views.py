from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from PIL import Image, ImageDraw, ImageFont
import random
import json
import hashlib
import os
import numpy as np


def _image_bg_color(image_path, darken=0.6):
    """Compute average color of an image and darken it by `darken` ratio.
    Returns hex string like '#2a1a0f'."""
    if not image_path or not os.path.exists(image_path):
        return ''
    try:
        img = Image.open(image_path).convert('RGBA')
        # Resize for performance: sample at most 200x200
        img.thumbnail((200, 200))
        arr = np.array(img)
        # Only non-transparent pixels
        mask = arr[:, :, 3] > 50
        if mask.any():
            r = int(arr[:, :, 0][mask].mean())
            g = int(arr[:, :, 1][mask].mean())
            b = int(arr[:, :, 2][mask].mean())
        else:
            r = int(arr[:, :, 0].mean())
            g = int(arr[:, :, 1].mean())
            b = int(arr[:, :, 2].mean())
        dark_r = max(0, int(r * (1 - darken)))
        dark_g = max(0, int(g * (1 - darken)))
        dark_b = max(0, int(b * (1 - darken)))
        return '#{0:02x}{1:02x}{2:02x}'.format(dark_r, dark_g, dark_b)
    except Exception:
        return ''

from .models import Category, Item, LearningProgress, QuizAttempt

# Emoji font for color extraction
_EMOJI_FONT_PATH = None
for _fp in ['C:/Windows/Fonts/seguiemj.ttf']:
    if os.path.exists(_fp):
        _EMOJI_FONT_PATH = _fp
        break


def _emoji_color(emoji, darken=0.7):
    """Extract average color from an emoji character and darken it by `darken` ratio.
    Returns hex string like '#3c2d12'. Falls back to hashed color on failure."""
    if not emoji or not _EMOJI_FONT_PATH:
        return _hash_tile_color(emoji or '?')

    cache_key = f'{emoji}:{darken}'
    if not hasattr(_emoji_color, '_cache'):
        _emoji_color._cache = {}
    if cache_key in _emoji_color._cache:
        return _emoji_color._cache[cache_key]

    try:
        font = ImageFont.truetype(_EMOJI_FONT_PATH, 80)
        img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), emoji, font=font, embedded_color=True)
        pixels = []
        for y in range(30, 90, 5):
            for x in range(30, 90, 5):
                r, g, b, a = img.getpixel((x, y))
                if a > 50:
                    pixels.append((r, g, b))
        if pixels:
            avg_r = int(sum(p[0] for p in pixels) / len(pixels))
            avg_g = int(sum(p[1] for p in pixels) / len(pixels))
            avg_b = int(sum(p[2] for p in pixels) / len(pixels))
            dark_r = max(0, int(avg_r * (1 - darken)))
            dark_g = max(0, int(avg_g * (1 - darken)))
            dark_b = max(0, int(avg_b * (1 - darken)))
            color = '#{0:02x}{1:02x}{2:02x}'.format(dark_r, dark_g, dark_b)
            _emoji_color._cache[cache_key] = color
            return color
    except Exception:
        pass

    fallback = _hash_tile_color(emoji)
    _emoji_color._cache[cache_key] = fallback
    return fallback


def _hash_tile_color(s):
    """Fallback color from hash of string."""
    TILE_COLORS = [
        '#3c2d12', '#2d2d2d', '#242424', '#422a0c',
        '#3f3621', '#2a2a2a', '#2d2118', '#423c3c',
        '#362d24', '#302418', '#23262b', '#2b1a1a',
        '#1e2b1e', '#2a2230', '#1a2330',
    ]
    h = hashlib.md5(s.encode()).hexdigest()
    idx = int(h[:8], 16) % len(TILE_COLORS)
    return TILE_COLORS[idx]


def _tile_color(item):
    h = hashlib.md5(str(item.id).encode()).hexdigest()
    idx = int(h[:8], 16) % len(TILE_COLORS)
    return TILE_COLORS[idx]


def index_view(request):
    categories = Category.objects.prefetch_related('items').all()
    return render(request, 'index.html', {'categories': categories})


def category_browse_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    from pypinyin import pinyin, Style
    items = sorted(
        list(category.items.all()),
        key=lambda it: pinyin(it.name, style=Style.TONE3)[0][0] if it.name else ''
    )

    # Attach color based on emoji for each item
    for item in items:
        item.color = _emoji_color(item.emoji or item.name)

    return render(request, 'category_browse.html', {
        'category': category,
        'items': items,
    })


def category_cards_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())
    items_json = json.dumps([{
        'id': it.id,
        'name': it.name,
        'english_name': it.english_name,
        'emoji': it.emoji,
        'fact': it.fact,
        'image': it.image.name if it.image else '',
        'bg_color': it.bg_color or '',
        'audio_zh': it.audio.name if it.audio else '',
        'audio_en': it.audio_en.name if it.audio_en else '',
        'audio_fact': it.audio_fact.name if it.audio_fact else '',
    } for it in items])
    return render(request, 'category_cards.html', {
        'category': category,
        'items': items,
        'items_json': items_json,
        'total': len(items),
    })


@login_required
def item_detail_api(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    progress, _ = LearningProgress.objects.get_or_create(
        user=request.user, item=item,
        defaults={'learned': True, 'view_count': 1}
    )
    if progress.id:
        progress.view_count += 1
        progress.learned = True
        progress.save()
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'english_name': item.english_name,
        'emoji': item.emoji,
        'fact': item.fact,
        'image': item.image.name if item.image else '',
        'image_position': item.image_position or 'center center',
        'audio_zh': item.audio.name if item.audio else '',
        'audio_en': item.audio_en.name if item.audio_en else '',
        'audio_fact': item.audio_fact.name if item.audio_fact else '',
    })


@login_required
def reset_visited(request, slug):
    """Reset visited state for all items in a category (client-side storage handle via localStorage)."""
    return JsonResponse({'status': 'ok'})


@login_required
def mark_viewed(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Item, id=item_id)
        progress, created = LearningProgress.objects.get_or_create(
            user=request.user, item=item,
            defaults={'learned': True, 'view_count': 1}
        )
        if not created:
            progress.view_count += 1
            progress.learned = True
            progress.save()
        return JsonResponse({'status': 'ok', 'view_count': progress.view_count})
    return JsonResponse({'status': 'error'}, status=400)


def category_quiz_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < 4:
        return render(request, 'category_quiz.html', {
            'category': category,
            'error': 'Need at least 4 items to create a quiz.',
        })

    quiz_type = request.GET.get('type', request.session.get('quiz_type', 'image_to_name'))
    request.session['quiz_type'] = quiz_type

    return render(request, 'category_quiz.html', {
        'category': category,
        'quiz_type': quiz_type,
        'item_count': len(items),
    })


@login_required
def quiz_question_api(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = list(category.items.all())

    if len(items) < 4:
        return JsonResponse({'error': 'Not enough items'}, status=400)

    quiz_type = request.GET.get('type', 'image_to_name')
    correct = random.choice(items)
    others = [i for i in items if i.id != correct.id]
    distractors = random.sample(others, min(3, len(others)))
    options = [correct] + distractors
    random.shuffle(options)

    data = {
        'correct_id': correct.id,
        'correct_name': correct.name,
        'image_url': correct.image.url if correct.image else None,
        'image_position': correct.image_position or 'center center',
        'emoji': correct.emoji,
        'quiz_type': quiz_type,
        'options': [{'id': i.id, 'name': i.name, 'english_name': i.english_name, 'image_url': i.image.url if i.image else None} for i in options],
    }
    return JsonResponse(data)


@login_required
@require_POST
def quiz_submit_batch(request, slug):
    category = get_object_or_404(Category, slug=slug)
    try:
        body = json.loads(request.body)
        total = body.get('total', 0)
        correct = body.get('correct', 0)
        quiz_type = body.get('quiz_type', 'image_to_name')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    QuizAttempt.objects.create(
        user=request.user,
        category=category,
        total=total,
        correct=correct,
        quiz_type=quiz_type,
    )

    return JsonResponse({'status': 'ok'})
