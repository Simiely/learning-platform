"""Search Unsplash API and download thumbnails for a given animal.

Usage:
    python download_unsplash.py <animal_name>

One API call, max 30 results, download only 20 thumbnails.
"""
import json, os, ssl, sys, time, urllib.request, urllib.parse

UNSPLASH_ACCESS_KEY = "uoHrNGA32at1Jz-TzFCNEf9pubYg9ZR2EM8UenvE5Os"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
})
opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))

def search(query, per_page=30, page=1):
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
