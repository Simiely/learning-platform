"""Space category seed data.

图片暂用 emoji 代替（img_file 留空），后续补充真实图片时再填入文件名。
分组：行星 / 恒星天体 / 航天器 / 天文现象
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SpaceItem:
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


SPACE_GROUPS = {
    "planet": "🪐 行星",
    "star": "⭐ 恒星天体",
    "spacecraft": "🚀 航天器",
    "phenomenon": "☄️ 天文现象",
}


ITEMS: list[SpaceItem] = [
    # ---- 行星 ----
    SpaceItem("水星", "mercury_2026080101", "Mercury", "🪐", "", "mercury.mp3",
              "水星是离太阳最近的行星，白天热得像烤箱，晚上又冷得像冰窖。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("金星", "venus_2026080102", "Venus", "🪐", "", "venus.mp3",
              "金星是夜空中最亮的星星，其实它的大气又厚又热，温度高得吓人。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("地球", "earth_2026080103", "Earth", "🌍", "", "earth.mp3",
              "地球是我们居住的星球，表面七成是海洋，是目前已知唯一有生命的星球。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("火星", "mars_2026080104", "Mars", "🔴", "", "mars.mp3",
              "火星看起来是红色的，因为表面有铁锈一样的物质，科学家在那里发现了水的痕迹。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("木星", "jupiter_2026080105", "Jupiter", "🪐", "", "jupiter.mp3",
              "木星是太阳系里最大的行星，肚子里能装下1300多个地球。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("土星", "saturn_2026080106", "Saturn", "🪐", "", "saturn.mp3",
              "土星有一圈漂亮的光环，光环其实是由无数冰块和岩石组成的。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("天王星", "uranus_2026080107", "Uranus", "🪐", "", "uranus.mp3",
              "天王星是躺着绕太阳转的行星，就像一颗打滚的皮球。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    SpaceItem("海王星", "neptune_2026080108", "Neptune", "🪐", "", "neptune.mp3",
              "海王星是太阳系里最远的行星，那里的风暴比地球上的台风还要猛烈。", "50% 50%", "50% 50%", "50% 50%", "planet"),
    # ---- 恒星天体 ----
    SpaceItem("太阳", "sun_2026080109", "Sun", "☀️", "", "sun.mp3",
              "太阳是一颗巨大的恒星，核心温度高达1500万度，给地球带来光和热。", "50% 50%", "50% 50%", "50% 50%", "star"),
    SpaceItem("月球", "moon_2026080110", "Moon", "🌙", "", "moon.mp3",
              "月球是地球的卫星，绕地球转一圈大约要一个月，它是离我们最近的星球。", "50% 50%", "50% 50%", "50% 50%", "star"),
    SpaceItem("星星", "star_2026080111", "Star", "⭐", "", "star.mp3",
              "夜空中闪烁的星星，很多其实是遥远的大太阳，它们离我们非常非常远。", "50% 50%", "50% 50%", "50% 50%", "star"),
    # ---- 航天器 ----
    SpaceItem("火箭", "rocket_2026080112", "Rocket", "🚀", "", "rocket.mp3",
              "火箭向下喷出巨大的火焰，把自己推向太空，是进入太空的重要工具。", "50% 50%", "50% 50%", "50% 50%", "spacecraft"),
    SpaceItem("卫星", "satellite_2026080113", "Satellite", "🛰️", "", "satellite.mp3",
              "人造卫星绕着地球转，帮我们看电视、导航、预报天气和拍照片。", "50% 50%", "50% 50%", "50% 50%", "spacecraft"),
    # ---- 天文现象 ----
    SpaceItem("彗星", "comet_2026080114", "Comet", "☄️", "", "comet.mp3",
              "彗星拖着长长的尾巴划过天空，尾巴其实是冰和尘埃被太阳风吹成的。", "50% 50%", "50% 50%", "50% 50%", "phenomenon"),
    SpaceItem("银河系", "galaxy_2026080115", "Milky Way", "🌌", "", "galaxy.mp3",
              "银河系是我们太阳系所在的星系，里面有几千亿颗星星，晚上抬头能看见一条亮带。", "50% 50%", "50% 50%", "50% 50%", "phenomenon"),
]
