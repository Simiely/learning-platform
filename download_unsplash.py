"""Download reference images from Unsplash for a given animal.

Usage:
    python download_unsplash.py <animal_name> [--count N] [--output DIR]

Example:
    python download_unsplash.py dragonfly --count 30 --output new-animals/references/dragonfly
"""
import os
import sys
import urllib.request
import json
import ssl
import time

UNSPLASH_ACCESS_KEY = "uoHrNGA32at1Jz-TzFCNEf9pubYg9ZR2EM8UenvE5Os"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
})
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))


def search_unsplash(query, per_page=30, page=1):
    """Search Unsplash API for photos. Costs API quota."""
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page={per_page}&page={page}"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}',
        'User-Agent': 'Mozilla/5.0'
    })
    resp = opener.open(req, timeout=30)
    data = json.loads(resp.read().decode())
    return data


def download_from_url(img_url, save_path):
    """Download image from a direct Unsplash CDN URL (free, no quota)."""
    req = urllib.request.Request(img_url, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    resp = opener.open(req, timeout=30)
    with open(save_path, 'wb') as f:
        f.write(resp.read())
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_unsplash.py <animal> [--count N] [--output DIR]")
        sys.exit(1)

    animal = sys.argv[1]
    count = 30
    output_dir = f"new-animals/references/{animal}"

    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg == '--count' and i + 1 < len(args):
            count = int(args[i + 1])
        elif arg == '--output' and i + 1 < len(args):
            output_dir = args[i + 1]

    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/2] Searching Unsplash for '{animal}'...")
    data = search_unsplash(animal, per_page=min(count, 30))
    total = data.get('total', 0)
    results = data.get('results', [])
    print(f"  Found {total} photos total, fetching page 1 ({len(results)} photos)")

    all_photos = list(results)

    # Fetch additional pages if needed
    pages_needed = (count + 29) // 30
    for p in range(2, min(pages_needed + 1, 4)):  # Max 3 pages to avoid rate limits
        if len(all_photos) >= count:
            break
        time.sleep(0.5)
        page_data = search_unsplash(animal, per_page=30, page=p)
        more_photos = page_data.get('results', [])
        all_photos.extend(more_photos)
        print(f"  Fetched page {p} ({len(more_photos)} photos)")

    # Limit to requested count
    all_photos = all_photos[:count]

    print(f"\n[2/2] Downloading {len(all_photos)} images to {output_dir}/...")
    success = 0
    for i, photo in enumerate(all_photos):
        photo_id = photo['id']
        # Use the 'regular' URL (~1080px wide) for good reference quality
        # CDN download is free - no API quota consumed
        img_url = photo['urls']['regular']
        ext = 'jpg'
        filename = f"{animal}_{i+1:02d}_{photo_id}.jpg"
        save_path = os.path.join(output_dir, filename)

        if os.path.exists(save_path):
            print(f"  [{i+1}/{len(all_photos)}] SKIP {filename} (exists)")
            success += 1
            continue

        try:
            download_from_url(img_url, save_path)
            print(f"  [{i+1}/{len(all_photos)}] OK {filename}")
            success += 1
            time.sleep(0.3)  # Be gentle to CDN
        except Exception as e:
            print(f"  [{i+1}/{len(all_photos)}] FAIL {filename}: {e}")

    print(f"\nDone! {success}/{len(all_photos)} images downloaded to {output_dir}/")


if __name__ == '__main__':
    main()
