"""Image processing utilities: visual-center detection, emoji color extraction.

These functions were extracted from apps/core/views.py to keep the views
module focused on request/response handling.

IMPORTANT — Image center detection caveat:
    detect_image_center() uses OpenCV saliency detection which finds the
    whole-object centroid, NOT the face. For animal photos, the face is
    usually in the upper portion. The card template compensates for this
    with an upward bias in its centerPos() helper.

    For hand-tuned positions, see seed_data.py ANIMALS table.
    Do NOT run `detect_centers --force` on seeded data.
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---- Emoji font path for color extraction ----
_EMOJI_FONT_PATH: Optional[str] = None
for _fp in [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto-emoji/NotoColorEmoji.ttf",
]:
    if os.path.exists(_fp):
        _EMOJI_FONT_PATH = _fp
        break


def detect_image_center(image_path: str) -> Optional[str]:
    """Detect visual focus centre using saliency detection first,
    then fall back to edge-weighted centroid.

    Returns CSS object-position string like '50% 30%' (top-left origin).
    Returns None if detection fails.
    """
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cx: Optional[float] = None
        cy: Optional[float] = None

        # Step 1: Saliency detection (finds prominent region — typically face/head)
        try:
            sal = cv2.saliency.StaticSaliencyFineGrained_create()
            _, sal_map = sal.computeSaliency(img)
            sal_f = sal_map.astype(np.float32)
            total = float(sal_f.sum())
            if total > 100:
                ys = np.arange(h, dtype=np.float32).reshape(-1, 1)
                xs = np.arange(w, dtype=np.float32).reshape(1, -1)
                cy = float((sal_f * ys).sum()) / total
                cx = float((sal_f * xs).sum()) / total
        except Exception:
            pass

        # Step 2: Edge-weighted centroid fallback
        if cx is None:
            edges = cv2.Canny(gray, 50, 150)
            ys = np.arange(h, dtype=np.float32).reshape(-1, 1)
            weight = 1.0 + 0.6 * (1.0 - ys / float(h))
            weighted = edges.astype(np.float32) * weight
            m00 = float(weighted.sum())
            if m00 > 10:
                xs = np.arange(w, dtype=np.float32).reshape(1, -1)
                ys = np.arange(h, dtype=np.float32).reshape(-1, 1)
                cx = float((weighted * xs).sum()) / m00
                cy = float((weighted * ys).sum()) / m00

        if cx is None or cy is None:
            return None

        pct_x = round(cx / float(w) * 100)
        pct_y = round(cy / float(h) * 100)
        pct_x = max(5, min(95, pct_x))
        pct_y = max(5, min(95, pct_y))
        return f"{pct_x}% {pct_y}%"
    except Exception:
        return None


def hash_tile_color(s: str) -> str:
    """Fallback colour derived from a hash of *s*."""
    TILE_COLORS = [
        "#3c2d12", "#2d2d2d", "#242424", "#422a0c",
        "#3f3621", "#2a2a2a", "#2d2118", "#423c3c",
        "#362d24", "#302418", "#23262b", "#2b1a1a",
        "#1e2b1e", "#2a2230", "#1a2330",
    ]
    h = hashlib.md5(s.encode(), usedforsecurity=False).hexdigest()
    idx = int(h[:8], 16) % len(TILE_COLORS)
    return TILE_COLORS[idx]


def emoji_color(emoji: str, darken: float = 0.7) -> str:
    """Extract average colour from an emoji character and darken it.

    Returns hex string like '#3c2d12'. Falls back to hashed colour on failure.
    """
    if not emoji or not _EMOJI_FONT_PATH:
        return hash_tile_color(emoji or "?")

    cache_key = f"{emoji}:{darken}"
    if not hasattr(emoji_color, "_cache"):
        emoji_color._cache: dict[str, str] = {}
    if cache_key in emoji_color._cache:
        return emoji_color._cache[cache_key]

    try:
        font = ImageFont.truetype(_EMOJI_FONT_PATH, 80)
        img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), emoji, font=font, embedded_color=True)
        pixels: list[tuple[int, int, int]] = []
        for y in range(30, 90, 5):
            for x in range(30, 90, 5):
                r, g, b, a = img.getpixel((x, y))
                if a > 50:
                    pixels.append((r, g, b))
        if pixels:
            avg_r = sum(p[0] for p in pixels) // len(pixels)
            avg_g = sum(p[1] for p in pixels) // len(pixels)
            avg_b = sum(p[2] for p in pixels) // len(pixels)
            dark_r = max(0, int(avg_r * (1 - darken)))
            dark_g = max(0, int(avg_g * (1 - darken)))
            dark_b = max(0, int(avg_b * (1 - darken)))
            color = "#{:02x}{:02x}{:02x}".format(dark_r, dark_g, dark_b)
            emoji_color._cache[cache_key] = color
            return color
    except Exception:
        pass

    fallback = hash_tile_color(emoji)
    emoji_color._cache[cache_key] = fallback
    return fallback


# Backward-compatible aliases for callers that import by old names
_detect_image_center = detect_image_center
_emoji_color = emoji_color
_hash_tile_color = hash_tile_color
