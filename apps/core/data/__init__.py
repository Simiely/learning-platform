"""分类数据汇总 — 所有分类的单一数据入口。

每个分类一个模块文件（animals.py / fruits.py / ...），本文件汇总为
CATEGORIES 列表，供 seed_data / seed_sync / sync_positions / check_data
统一遍历使用。

新增分类步骤：
1. 新建 apps/core/data/<slug>.py，定义 ITEMS 列表 + <SLUG>_GROUPS 配置
2. 在本文件 CATEGORIES 中注册一项
3. 无需改任何命令/视图代码
"""
from dataclasses import dataclass, field
from typing import Any

from .animals import ANIMALS, ANIMAL_GROUPS
from .fruits import FRUIT_GROUPS, ITEMS as FRUITS


@dataclass(frozen=True)
class CardItem:
    """通用卡片条目（兼容旧 Animal 的 11 字段）。"""
    name: str
    code: str
    english_name: str
    emoji: str
    img_file: str
    audio_file: str
    fact: str
    image_position: str = "50% 50%"
    image_position_ipad_portrait: str = "50% 50%"
    image_position_ipad_landscape: str = "50% 50%"
    group: str = ""


# 向后兼容：旧代码 import 的 Animal 就是 CardItem
Animal = CardItem


@dataclass(frozen=True)
class CategoryData:
    """一个分类的完整定义（名称/图标/描述/分组/条目）。"""
    slug: str
    name: str
    icon: str
    description: str
    sort_order: int
    groups: dict[str, str]
    items: list[Any]


CATEGORIES: list[CategoryData] = [
    CategoryData(
        slug="animals",
        name="动物",
        icon="🐾",
        description="认识各种动物",
        sort_order=1,
        groups=ANIMAL_GROUPS,
        items=ANIMALS,
    ),
    CategoryData(
        slug="fruits",
        name="果蔬",
        icon="🍎",
        description="认识常见的水果和蔬菜",
        sort_order=2,
        groups=FRUIT_GROUPS,
        items=FRUITS,
    ),
]

# 兼容旧导入：from apps.core.data import ANIMALS
ANIMALS_ALL: list[CardItem] = ANIMALS
ANIMALS = ANIMALS  # noqa: F811 — 保持旧名可用（动物数据）
