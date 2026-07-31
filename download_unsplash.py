"""Search Unsplash API and download thumbnails for a given animal.

Usage:
    python download_unsplash.py <animal_name>

One API call, max 30 results, download only 20 thumbnails.

API Key 通过环境变量 UNSPLASH_ACCESS_KEY 提供（不入库）。
代理地址通过 HTTPS_PROXY / HTTP_PROXY 提供；未设置时直连。
"""
import json, os, ssl, sys, time, urllib.request, urllib.parse

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

_PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or ""
if _PROXY:
    proxy_handler = urllib.request.ProxyHandler({
        'http': _PROXY,
        'https': _PROXY,
    })
else:
    proxy_handler = urllib.request.ProxyHandler({})

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))

def search(query, per_page=30, page=1):
    if not UNSPLASH_ACCESS_KEY:
        raise RuntimeError("UNSPLASH_ACCESS_KEY 环境变量未设置")
    encoded = urllib.parse.quote(query)
    url = f"https://api.unsplash.com/search/photos?query={encoded}&per_page={per_page}&page={page}"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}',
        'User-Agent': 'Mozilla/5.0'
    })
    resp = opener.open(req, timeout=30)
    return json.loads(resp.read().decode())

def download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = opener.open(req, timeout=30).read()
    with open(path, 'wb') as f:
        f.write(data)

def main():
    animal = sys.argv[1] if len(sys.argv) > 1 else "deer"
    safe_name = animal.replace(" ", "-")
    out_dir = f"new-animals/references/{safe_name}"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Searching Unsplash for '{animal}' (fetching up to 30, downloading 20)...")
    data = search(animal)
    photos = data.get('results', [])
    print(f"Found {data.get('total',0)} total, got {len(photos)} photos")

    for i, p in enumerate(photos[:20], 1):
        pid = p['id']
        alt = (p.get('alt_description') or p.get('description') or '')[:50]
        thumb = p['urls']['small']  # ~400px, free CDN download
        path = os.path.join(out_dir, f"u{i:02d}_{pid}.jpg")
        try:
            download(thumb, path)
            print(f"  [{i}/20] OK {pid}  {alt}")
        except Exception as e:
            print(f"  [{i}/20] FAIL {pid}: {e}")
        time.sleep(0.3)

    print(f"\nDone! Saved to {out_dir}/")

if __name__ == "__main__":
    main()
