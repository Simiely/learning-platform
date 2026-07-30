"""
第6批动物图片下载脚本 - 从 Pexels 下载高清原图
用法: python scripts/download_batch6.py

下载的图片将保存到 media/images/ 目录
"""

import urllib.request
import ssl
import os
import sys
import time

# 确保 workdir 是项目根目录
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 每只动物推荐的 Pexels 图片 ID ---
# 选图原则：动物面部清晰、背景干净、适合儿童闪卡
ANIMALS = {
    'jellyfish': {
        'pid': 5472598,
        'filename': 'jellyfish.jpg',
        'credit': 'Ryutaro Tsukata',
        'desc': 'Moon jellyfish floating in water',
    },
    'starfish': {
        'pid': 2540698,
        'filename': 'starfish.jpg',
        'credit': 'Themarque',
        'desc': 'Close-up of purple and orange starfish',
    },
    'bat': {
        'pid': 6396384,
        'filename': 'bat.jpg',
        'credit': 'Vincent Ma Janssen',
        'desc': 'Close-up photo of sleeping bat',
    },
    'sloth': {
        'pid': 16408572,
        'filename': 'sloth.jpg',
        'credit': 'Shuvalova Natalia',
        'desc': 'Sloth hanging on tree',
    },
    'otter': {
        'pid': 57466,
        'filename': 'otter.jpg',
        'credit': 'Pixabay',
        'desc': 'Brown otter near green grass',
    },
    'mouse': {
        'pid': 16206020,
        'filename': 'mouse.jpg',
        'credit': 'Lonnyphotography',
        'desc': 'Mouse close-up',
    },
}

def download_image(animal_key, info):
    """下载 Pexels 高清原图"""
    pid = info['pid']
    filename = info['filename']
    
    # Pexels 高清原图 URL（不加 ?w= 参数 = 原图）
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"
    
    dest_dir = os.path.join('media', 'images')
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    
    # 跳过已存在的文件
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        print(f'  [SKIP] {filename} already exists ({size/1024:.0f} KB)')
        return True
    
    print(f'  Downloading {filename} ({info["desc"]})...', end=' ', flush=True)
    
    # 绕过 SSL 验证（Pexels CDN 可能走代理）
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl_ctx),
        urllib.request.ProxyHandler({}),  # 绕过系统代理
    )
    
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36'
        }
    )
    
    try:
        data = opener.open(req, timeout=60).read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        print(f'OK ({len(data)/1024:.0f} KB)')
        return True
    except Exception as e:
        print(f'FAILED: {e}')
        return False


def main():
    print('=' * 60)
    print('  第6批动物图片下载（Pexels 高清原图）')
    print('=' * 60)
    print()
    
    success = 0
    fail = 0
    
    for key, info in ANIMALS.items():
        print(f'[{key}]')
        if download_image(key, info):
            success += 1
        else:
            fail += 1
        time.sleep(1)  # 请求间隔，避免被限流
    
    print()
    print('=' * 60)
    print(f'  完成: {success} 成功, {fail} 失败')
    print(f'  图片保存在: media/images/')
    print('=' * 60)
    
    if fail > 0:
        print()
        print('下载失败的图片，可以手动访问以下链接下载：')
        for key, info in ANIMALS.items():
            pid = info['pid']
            url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"
            print(f'  {info["filename"]}: {url}')
    
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
