"""Shared view helpers (sorting, progress tracking).

业务层公共服务：供多个视图复用，避免重复逻辑。
"""

from __future__ import annotations

from typing import Any, Iterable

from pypinyin import Style, pinyin


def sort_by_pinyin(items: Iterable[Any]) -> list[Any]:
    """按中文名拼音（带声调）排序，空名排最后。个别字符解析失败时回退空串。"""
    def _key(it: Any) -> str:
        if not it.name:
            return ""
        try:
            return pinyin(it.name, style=Style.TONE3)[0][0]
        except Exception:
            return ""

    return sorted(list(items), key=_key)


def pinyin_initial(name: str) -> str:
    """取中文名拼音首字母（大写 A-Z）；非字母或失败时返回 '#'。"""
    if not name:
        return "#"
    try:
        initial = pinyin(name, style=Style.FIRST_LETTER)[0][0][0].upper()
        return initial if initial.isalpha() else "#"
    except Exception:
        return "#"


def mark_item_viewed(user, item: Any) -> None:
    """记录用户查看某条目（原子递增 view_count）。未登录用户为 no-op。"""
    if not user.is_authenticated:
        return
    from .models import LearningProgress
    from django.db.models import F

    progress, created = LearningProgress.objects.get_or_create(
        user=user,
        item=item,
        defaults={"learned": True, "view_count": 1},
    )
    if not created:
        progress.view_count = F("view_count") + 1
        progress.learned = True
        progress.save(update_fields=["view_count", "learned"])
