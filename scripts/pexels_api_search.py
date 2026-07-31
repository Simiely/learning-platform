"""Search Pexels API and download thumbnails for a given animal.

API Key 通过环境变量 PEXELS_KEY 提供（不入库）。
代理地址通过 HTTPS_PROXY / HTTP_PROXY 提供；未设置时直连。
"""
import json, os, ssl, sys, time, urllib.request, urllib.parse

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")

_PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or ""
if _PROXY:
    proxy_handler = urllib.request.ProxyHandler({
        'http': _PROXY,
        'https': _PROXY,
    })
else:
    proxy_handler = urllib.request.ProxyHandler({})

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ssl_ctx))

def search(query, per_page=80):
    if not PEXELS_KEY:
        raise RuntimeError("PEXELS_KEY 环境变量未设置")
    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page={per_page}&page=1"
    req = urllib.request.Request(url, headers={
        'Authorization': PEXELS_KEY,
        'User-Agent': 'Mozilla/5.0'
    })
    resp = opener.open(req, timeout=30)
    data = json.loads(resp.read().decode())
    return data.get('photos', [])

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

    print(f"Searching Pexels for '{animal}' (fetching up to 80 candidates, downloading 20)...")
    photos = search(animal)
    print(f"Found {len(photos)} photos, downloading 20 thumbnails...")

    for i, p in enumerate(photos[:20], 1):
        pid = p['id']
        alt = (p.get('alt') or '')[:50]
        thumb = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?w=400"
        path = os.path.join(out_dir, f"{i:02d}_{pid}.jpg")
        try:
            download(thumb, path)
            print(f"  [{i}/20] OK {pid}  {alt}")
        except Exception as e:
            print(f"  [{i}/20] FAIL {pid}: {e}")
        time.sleep(0.3)

    print(f"\nDone! Saved to {out_dir}/")

if __name__ == "__main__":
    main()
