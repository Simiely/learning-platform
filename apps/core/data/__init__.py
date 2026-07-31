"""分类数据汇总 — 所有分类的单一数据入口。

每个分类一个模块文件（animals.py / fruits.py / ...），本文件汇总为
CATEGORIES 列表，供 seed_data / seed_sync / sync_positions / check_data
统一遍历使用。

新增分类步骤：
1. 新建 apps/core/data/<slug>.py，定义 ITEMS 列表 + <SLUG>_GROUPS 配置
2. 在本文件 CATEGORIES 中注册一项
3. 无需改任何命令/视图代码

注意：CardItem 必须先于分类文件导入定义（分类文件用 from . import CardItem）。
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CardItem:
    """通用卡片条目（兼容旧 Animal 的 11 字段，所有分类共用）。"""
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


# ---- 导入各分类数据（CardItem 已定义，分类文件可 from . import CardItem）----
from .animals import ANIMALS, ANIMAL_GROUPS
from .dinosaurs import DINOSAUR_GROUPS, ITEMS as DINOSAURS
from .fruits import FRUIT_GROUPS, ITEMS as FRUITS
from .jobs import JOB_GROUPS, ITEMS as JOBS
from .plants import PLANT_GROUPS, ITEMS as PLANTS
from .space import SPACE_GROUPS, ITEMS as SPACE
from .vehicles import VEHICLE_GROUPS, ITEMS as VEHICLES


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
    CategoryData(
        slug="vehicles",
        name="交通工具",
        icon="🚗",
        description="认识路上的、水里游的和天上飞的交通工具",
        sort_order=3,
        groups=VEHICLE_GROUPS,
        items=VEHICLES,
    ),
    CategoryData(
        slug="dinosaurs",
        name="恐龙",
        icon="🦖",
        description="认识远古时代的恐龙",
        sort_order=4,
        groups=DINOSAUR_GROUPS,
        items=DINOSAURS,
    ),
    CategoryData(
        slug="space",
        name="太空",
        icon="🚀",
        description="认识行星、恒星和航天器",
        sort_order=5,
        groups=SPACE_GROUPS,
        items=SPACE,
    ),
    CategoryData(
        slug="plants",
        name="花卉植物",
        icon="🌹",
        description="认识美丽的花卉和植物",
        sort_order=6,
        groups=PLANT_GROUPS,
        items=PLANTS,
    ),
    CategoryData(
        slug="jobs",
        name="职业",
        icon="👨‍🚒",
        description="认识各种各样的职业",
        sort_order=7,
        groups=JOB_GROUPS,
        items=JOBS,
    ),
]

# 兼容旧导入：from apps.core.data import ANIMALS
ANIMALS_ALL: list[CardItem] = ANIMALS
ANIMALS = ANIMALS  # noqa: F811 — 保持旧名可用（动物数据）
