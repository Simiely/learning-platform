"""
批量生成动物音频文件（edge-tts）。

为每只动物生成 3 个 mp3：
  media/audio/<base>.mp3       中文名    (zh-CN-XiaoxiaoNeural)
  media/audio_en/<base>.mp3    英文名    (en-US-JennyNeural)
  media/audio_fact/<base>.mp3  中文科普  (zh-CN-XiaoxiaoNeural)

依赖：pip install edge-tts
网络：若所在环境需代理才能访问外网，先 export HTTPS_PROXY=http://<host>:<port>

用法：
  python gen_audio.py            # 生成 data.py ANIMALS 里的全部动物
  python gen_audio.py ant ladybug # 仅生成指定基名（可选）

注意：
  - 数据来源统一为 apps/core/data.py（与 seed_data/seed_sync 共用单一数据源）。
  - 图片/音频的"基名"就是 data.py 中 img_file/audio_file 的基名。
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

# 从单一数据源读取全部动物（base, 中文名, 英文名, 科普文案）
def _animals():
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from apps.core.data import ANIMALS

    return [
        (Path(a.img_file).stem, a.name, a.english_name, a.fact)
        for a in ANIMALS
    ]


ANIMALS = _animals()


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
