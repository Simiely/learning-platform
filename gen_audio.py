"""
批量生成动物音频文件（edge-tts）。

为每只动物生成 3 个 mp3：
  media/audio/<base>.mp3       中文名    (zh-CN-XiaoxiaoNeural)
  media/audio_en/<base>.mp3    英文名    (en-US-JennyNeural)
  media/audio_fact/<base>.mp3  中文科普  (zh-CN-XiaoxiaoNeural)

依赖：pip install edge-tts
网络：若所在环境需代理才能访问外网，先 export HTTPS_PROXY=http://<host>:<port>

用法：
  python gen_audio.py            # 生成 ANIMALS 列表里的全部动物
  python gen_audio.py ant ladybug # 仅生成指定基名（可选）

注意：
  - 图片/音频的"基名"必须与 seed_data.py 中该动物的 img_file/audio_file 基名一致
    （例如 seed 用 'ant.jpg' → 这里基名 'ant'）。
  - 新增批次时，在下方 ANIMALS 列表追加 (base, 中文名, 英文名, 科普文案) 即可。
  - 科普文案建议与 ANIMALS.md / seed_data.py 中保持一致。
"""
import asyncio
import os
import sys
from pathlib import Path

from edge_tts import Communicate

# 自动推导 media 目录：本脚本应放在 learning-platform/ 根目录
BASE = Path(__file__).resolve().parent / "media"
ZH = "zh-CN-XiaoxiaoNeural"
EN = "en-US-JennyNeural"

# (base, chinese_name, english_name, fact_text)
# base 必须与 seed_data.py 里对应动物的图片/音频基名一致
ANIMALS = [
    ("deer",      "梅花鹿",   "Deer",     "梅花鹿在夏天身上有白色斑点像梅花，到了冬天斑点就消失了。只有雄鹿长角，每年都会脱落重新长。"),
    ("brownbear", "棕熊",    "Brown Bear","棕熊是体型最大的熊之一，冬天会冬眠。它们跑步速度能达到每小时50公里，比人快得多。"),
    ("gorilla",   "大猩猩",  "Gorilla",  "大猩猩是最大的灵长类动物，和人类有98%的基因相同。它们会用手语和人类交流。"),
    ("peacock",   "孔雀",    "Peacock",  "孔雀开屏时尾巴像一把巨大的扇子，上面有像眼睛一样的花纹。开屏是为了吸引雌孔雀。"),
    ("flamingo",  "火烈鸟",  "Flamingo", "火烈鸟为什么是粉色的？因为它们吃的虾和藻类里有红色素。它们单脚站立睡觉也不会倒。"),
    ("swan",      "天鹅",    "Swan",     "天鹅是优雅的鸟类，终身只有一个伴侣。它们飞行时能飞到9000米高，是飞得最高的鸟类之一。"),
    ("firefly",   "萤火虫",  "Firefly",  "萤火虫的尾部会发光，这是它们在寻找伴侣的信号。一只萤火虫的光由几十种化学反应控制。"),
    ("spider",    "蜘蛛",    "Spider",   "蜘蛛不是昆虫，属于蛛形纲。它们吐的丝比钢铁还要坚韧，有些蜘蛛能织出直径2米的大网。"),
    ("ant",       "蚂蚁",     "Ant",      "蚂蚁是地球上数量最多的昆虫之一，一个蚁群可以有几十万只蚂蚁。它们能搬起比自己重50倍的东西。"),
    ("ladybug",   "瓢虫",     "Ladybug",  "瓢虫背上有黑色斑点，7个点的最常见。它们是农民的好朋友，因为爱吃蚜虫这种害虫。"),
    ("chameleon", "变色龙",   "Chameleon","变色龙变颜色不只是为了伪装，还为了表达情绪和调节体温。它们的眼睛可以独立转动！"),
    ("lizard",    "蜥蜴",     "Lizard",   "蜥蜴的尾巴断了还能重新长出来。它们在墙上爬行靠的是脚上细小的毛，能产生吸附力。"),
    ("dragonfly", "蜻蜓",     "Dragonfly","蜻蜓是飞行高手，能向前飞、向后飞、悬停在空中。它们的眼睛由3万多只小眼睛组成！"),
    ("snail",     "蜗牛",     "Snail",    "蜗牛是地球上最慢的动物之一，但它们有两万六千多颗牙齿！蜗牛壳是随着身体一起长大的。"),
    ("hedgehog",  "刺猬",     "Hedgehog", "刺猬身上有大约5000根刺，遇到危险时会把身体卷成球。它们吃虫子，是花园里的小卫士。"),
    ("hamster",   "仓鼠",     "Hamster",  "仓鼠的脸颊有像口袋一样的颊囊，可以塞满食物带回窝里。它们是很多小朋友养的第一种宠物。"),
    ("seaturtle", "海龟",     "Sea Turtle","海龟已经在地球上生活了超过1亿年，它们可以活到80岁以上。雌海龟会回到自己出生的海滩产卵。"),
    ("octopus",   "章鱼",     "Octopus",  "章鱼有三个心脏、九个大脑，血液是蓝色的。它们非常聪明，能打开瓶盖、模仿其他动物。"),
    ("seahorse",  "海马",     "Seahorse", "海马爸爸负责孵宝宝！雌海马把卵产在雄海马的育儿袋里，爸爸怀孕生小海马。"),
    ("sealion",   "海狮",     "Sea Lion", "海狮是海洋馆的明星，它们用鳍状肢在陆地上行走，在水里能憋气超过10分钟。"),
]


async def gen_one(text, voice, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    last = None
    for _ in range(3):
        try:
            comm = Communicate(text, voice)
            await comm.save(out_path)
            if os.path.getsize(out_path) > 0:
                return True
        except Exception as e:  # noqa: BLE001
            last = e
    print(f"  FAIL {out_path}: {last}")
    return False


async def main():
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    items = [a for a in ANIMALS if only is None or a[0] in only]
    if only is not None:
        missing = only - {a[0] for a in ANIMALS}
        if missing:
            print(f"WARNING: base not in ANIMALS list: {sorted(missing)}")

    total = ok = 0
    for base, zh_name, en_name, fact in items:
        tasks = [
            (BASE / "audio" / f"{base}.mp3",      zh_name, ZH),
            (BASE / "audio_en" / f"{base}.mp3",   en_name, EN),
            (BASE / "audio_fact" / f"{base}.mp3", fact,    ZH),
        ]
        for out_path, text, voice in tasks:
            total += 1
            if await gen_one(text, voice, str(out_path)):
                ok += 1
                print(f"  OK  {os.path.relpath(out_path, BASE)}")
    print(f"\nDONE: {ok}/{total} files generated")


if __name__ == "__main__":
    asyncio.run(main())
