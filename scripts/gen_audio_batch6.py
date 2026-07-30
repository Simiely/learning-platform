"""
第6批动物音频生成脚本 - 使用 edge-tts
用法:
  1. pip install edge-tts
  2. python scripts/gen_audio_batch6.py

将生成 3 种音频文件到 media/audio/, media/audio_en/, media/audio_fact/
"""

import subprocess
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ANIMALS = [
    # (中文名, 中文读音, 英文名, 科普知识)
    ('水母', 'shuǐ mǔ', 'Jellyfish',
     '水母没有大脑、没有心脏、没有血液，但它们已经在地球上生活了超过6亿年。有些水母甚至可以永生。'),
    ('海星', 'hǎi xīng', 'Starfish',
     '海星被切掉一条胳膊可以重新长出来，被切掉的胳膊也能长成一只全新的海星！'),
    ('蝙蝠', 'biān fú', 'Bat',
     '蝙蝠是唯一会飞的哺乳动物。它们在黑暗中用超声波导航，能在完全看不见的情况下抓蚊子吃。'),
    ('树懒', 'shù lǎn', 'Sloth',
     '树懒是世界上最慢的哺乳动物，每秒只能移动几厘米。它们大部分时间倒挂在树上，一周才下一次树。'),
    ('水獭', 'shuǐ tǎ', 'Otter',
     '水獭是非常爱玩的小动物，经常仰面躺在水面上玩耍。它们有最喜欢的石头，用来敲开贝壳。'),
    ('老鼠', 'lǎo shǔ', 'Mouse',
     '老鼠非常聪明，能学会走迷宫。它们的门牙一生都在生长，所以需要不停地咬东西来磨牙。'),
]

AUDIO_DIRS = {
    'zh': 'media/audio',
    'en': 'media/audio_en',
    'fact': 'media/audio_fact',
}

def generate_audio(animal):
    cn_name, cn_pron, en_name, fact = animal
    fname = f'{en_name.lower().replace(" ", "")}.mp3'
    
    print(f'\n[{cn_name} / {en_name}]')
    
    # 中文名音频
    zh_path = os.path.join(AUDIO_DIRS['zh'], fname)
    if not os.path.exists(zh_path):
        cmd = f'edge-tts --voice zh-CN-XiaoxiaoNeural --text "{cn_name}" --write-media "{zh_path}"'
        print(f'  zh: {cn_name} -> {fname}')
        subprocess.run(cmd, shell=True, check=True)
    else:
        print(f'  zh: [SKIP] {fname} exists')
    
    # 英文名音频
    en_path = os.path.join(AUDIO_DIRS['en'], fname)
    if not os.path.exists(en_path):
        cmd = f'edge-tts --voice en-US-JennyNeural --text "{en_name}" --write-media "{en_path}"'
        print(f'  en: {en_name} -> {fname}')
        subprocess.run(cmd, shell=True, check=True)
    else:
        print(f'  en: [SKIP] {fname} exists')
    
    # 科普知识音频
    fact_path = os.path.join(AUDIO_DIRS['fact'], fname)
    if not os.path.exists(fact_path):
        cmd = f'edge-tts --voice zh-CN-XiaoxiaoNeural --text "{fact}" --write-media "{fact_path}"'
        print(f'  fact: {fact[:30]}... -> {fname}')
        subprocess.run(cmd, shell=True, check=True)
    else:
        print(f'  fact: [SKIP] {fname} exists')


def main():
    print('=' * 60)
    print('  第6批动物音频生成（edge-tts）')
    print('=' * 60)
    
    # 确保目录存在
    for d in AUDIO_DIRS.values():
        os.makedirs(d, exist_ok=True)
    
    for animal in ANIMALS:
        generate_audio(animal)
    
    print()
    print('=' * 60)
    print('  音频生成完成！')
    print('  共 3 种语言 x 6 只 = 18 个音频文件')
    print('=' * 60)


if __name__ == '__main__':
    main()
