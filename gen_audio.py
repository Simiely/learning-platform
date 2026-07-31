"""
批量生成动物音频文件（edge-tts）。

为每只动物生成 3 个 mp3：
  media/audio/<base>.mp3       中文名    (zh-CN-XiaoxiaoNeural)
  media/audio_en/<base>.mp3    英文名    (en-US-JennyNeural)
  media/audio_fact/<base>.mp3  中文科普  (zh-CN-XiaoxiaoNeural)

依赖：pip install edge-tts
网络：若所在环境需代理才能访问外网，先 export HTTPS_PROXY=http://<host>:<port>

用法：
  python gen_audio.py                          # 生成全部分类的音频（慎用，会重新生成已有音频）
  python gen_audio.py --category fruits        # 只生成指定分类（推荐，加新分类时用）
  python gen_audio.py --category fruits apple  # 只生成该分类下指定基名
  python gen_audio.py ant ladybug              # 仅生成指定基名（不指定分类时全库搜索）

注意：
  - 数据来源统一为 apps/core/data/（与 seed_data/seed_sync 共用单一数据源）。
  - 图片/音频的"基名"就是 apps/core/data/ 中条目 img_file/audio_file 的基名。
  - ⚠️ 动物等已有分类的音频不要用无参数全量生成——会覆盖已有文件，
    中途失败会留下 0 字节损坏文件。加新分类用 --category 只生成新增部分。
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

from edge_tts import Communicate

# 自动推导 media 目录：本脚本应放在 learning-platform/ 根目录
BASE = Path(__file__).resolve().parent / "media"
ZH = "zh-CN-XiaoxiaoNeural"
EN = "en-US-JennyNeural"


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
    # 解析参数：--category <slug> 可选，其余位置参数按基名过滤
    parser = argparse.ArgumentParser(description="Generate animal/card audio via edge-tts")
    parser.add_argument("--category", metavar="SLUG", help="only generate this category (e.g. fruits)")
    parser.add_argument("bases", nargs="*", help="optional base-name filter")
    args = parser.parse_args()

    only_bases = set(args.bases) if args.bases else None

    # 按分类过滤
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from apps.core.data import CATEGORIES

    if args.category:
        cats = [c for c in CATEGORIES if c.slug == args.category]
        if not cats:
            print(f"ERROR: unknown category '{args.category}'. Available: {[c.slug for c in CATEGORIES]}")
            sys.exit(1)
        items = [
            (Path(a.audio_file or a.img_file).stem, a.name, a.english_name, a.fact)
            for a in cats[0].items
        ]
    else:
        items = [
            (Path(a.audio_file or a.img_file).stem, a.name, a.english_name, a.fact)
            for cat in CATEGORIES for a in cat.items
        ]

    if only_bases is not None:
        items = [a for a in items if a[0] in only_bases]
        missing = only_bases - {a[0] for a in items}
        if missing:
            print(f"WARNING: base not found: {sorted(missing)}")

    print(f"Generating {len(items)} items, 3 files each...")
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
