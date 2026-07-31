"""Dinosaurs category seed data.

图片暂用 emoji 代替（img_file 留空），后续补充真实图片时再填入文件名。
分组：食肉 / 食草 / 会飞
条目使用共享 CardItem（见 __init__.py）。
"""
from . import CardItem


DINOSAUR_GROUPS = {
    "carnivore": "🦖 食肉恐龙",
    "herbivore": "🦕 食草恐龙",
    "flying": "🦇 会飞恐龙",
}


ITEMS: list[CardItem] = [
    # ---- 食肉恐龙 ----
    CardItem("霸王龙", "t_rex_2026080101", "Tyrannosaurus Rex", "🦖", "", "t_rex.mp3",
             "霸王龙是恐龙中的霸主，牙齿像香蕉一样大，咬合力比狮子还要强10倍。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    CardItem("迅猛龙", "velociraptor_2026080102", "Velociraptor", "🦖", "", "velociraptor.mp3",
             "迅猛龙跑得特别快，脚上有像镰刀一样锋利的钩爪，是非常聪明的猎手。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    CardItem("棘龙", "spinosaurus_2026080103", "Spinosaurus", "🦖", "", "spinosaurus.mp3",
             "棘龙背上有一片像帆一样的大脊，它还会游泳，喜欢吃鱼。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    CardItem("异特龙", "allosaurus_2026080104", "Allosaurus", "🦖", "", "allosaurus.mp3",
             "异特龙是侏罗纪时期的顶级猎手，可能会成群结队一起捕猎。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    CardItem("食肉牛龙", "carnotaurus_2026080105", "Carnotaurus", "🦖", "", "carnotaurus.mp3",
             "食肉牛龙头上有两个小小的角，前臂非常短小，跑起来速度却很快。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    CardItem("南方巨兽龙", "giganotosaurus_2026080106", "Giganotosaurus", "🦖", "", "giganotosaurus.mp3",
             "南方巨兽龙比霸王龙还要长，生活在今天的南美洲，是巨大的食肉恐龙。", "50% 50%", "50% 50%", "50% 50%", "carnivore"),
    # ---- 食草恐龙 ----
    CardItem("三角龙", "triceratops_2026080107", "Triceratops", "🦕", "", "triceratops.mp3",
             "三角龙头上有三个尖角，脖子上还有一块大骨板，用来保护自己。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("剑龙", "stegosaurus_2026080108", "Stegosaurus", "🦕", "", "stegosaurus.mp3",
             "剑龙背上长着两排三角形的骨板，尾巴末端还有四根尖刺。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("腕龙", "brachiosaurus_2026080109", "Brachiosaurus", "🦕", "", "brachiosaurus.mp3",
             "腕龙是最高大的恐龙之一，脖子长长的，像长颈鹿一样吃树顶的叶子。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("梁龙", "diplodocus_2026080110", "Diplodocus", "🦕", "", "diplodocus.mp3",
             "梁龙的脖子和尾巴都非常长，尾巴甩起来像鞭子一样有力。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("甲龙", "ankylosaurus_2026080111", "Ankylosaurus", "🦕", "", "ankylosaurus.mp3",
             "甲龙全身披着厚厚的硬甲，尾巴末端像一个大锤子，能击退敌人。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("肿头龙", "pachycephalosaurus_2026080112", "Pachycephalosaurus", "🦕", "", "pachycephalosaurus.mp3",
             "肿头龙头顶的骨头又厚又硬，像戴了一顶头盔，雄龙会用它来打架。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("副栉龙", "parasaurolophus_2026080113", "Parasaurolophus", "🦕", "", "parasaurolophus.mp3",
             "副栉龙头顶有一根长长的管状冠，能发出响亮的声音来和同伴交流。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    CardItem("禽龙", "iguanodon_2026080114", "Iguanodon", "🦕", "", "iguanodon.mp3",
             "禽龙的拇指像钉子一样又尖又硬，可以用来防御敌人的攻击。", "50% 50%", "50% 50%", "50% 50%", "herbivore"),
    # ---- 会飞恐龙 ----
    CardItem("翼手龙", "pterodactyl_2026080115", "Pterodactyl", "🦇", "", "pterodactyl.mp3",
             "翼手龙是能飞的爬行动物，翅膀是一层皮膜，展开比两个小朋友还宽。", "50% 50%", "50% 50%", "50% 50%", "flying"),
    CardItem("无齿翼龙", "pteranodon_2026080116", "Pteranodon", "🦇", "", "pteranodon.mp3",
             "无齿翼龙的嘴巴里没有牙齿，头顶长着长长的冠，在海边抓鱼吃。", "50% 50%", "50% 50%", "50% 50%", "flying"),
]
