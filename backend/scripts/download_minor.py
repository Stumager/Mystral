import os
import time

import requests

BASE_API = "https://en.wikipedia.org/w/api.php"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "tarot")
os.makedirs(OUT_DIR, exist_ok=True)

SUITS = [
    ("Wands", 22),
    ("Cups", 36),
    ("Swords", 50),
    ("Pents", 64),
]

def resolve_urls(filenames: list[str]) -> dict[str, str]:
    titles = "|".join(f"File:{f}" for f in filenames)
    r = requests.get(BASE_API, params={
        "action": "query",
        "titles": titles,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }, headers={"User-Agent": "Mystral/1.0"}, timeout=15)
    data = r.json()
    result = {}
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "").replace("File:", "")
        info = page.get("imageinfo", [{}])
        if info and "url" in info[0]:
            result[title] = info[0]["url"]
    return result

all_files = []
id_map = {}

for suit, start_id in SUITS:
    for i in range(1, 15):
        fname = f"{suit}{i:02d}.jpg"
        card_id = start_id + i - 1
        all_files.append(fname)
        id_map[fname] = card_id

batch1 = all_files[:28]
batch2 = all_files[28:]

print("Resolving URLs batch 1...")
urls = resolve_urls(batch1)
time.sleep(1)
print("Resolving URLs batch 2...")
urls.update(resolve_urls(batch2))

print(f"Resolved {len(urls)} of {len(all_files)} URLs")

downloaded = 0
skipped = 0
failed = 0

for fname, card_id in id_map.items():
    out_path = os.path.join(OUT_DIR, f"{card_id}.jpg")
    if os.path.exists(out_path):
        skipped += 1
        continue

    url = urls.get(fname)
    if not url:
        print(f"FAIL {card_id} ({fname}): no URL resolved")
        failed += 1
        continue

    try:
        r = requests.get(url, headers={"User-Agent": "Mystral/1.0"}, timeout=15)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(r.content)
            downloaded += 1
            print(f"OK {card_id} ({fname})")
        else:
            print(f"FAIL {card_id} ({fname}): HTTP {r.status_code}")
            failed += 1
    except Exception as e:
        print(f"FAIL {card_id} ({fname}): {e}")
        failed += 1

    time.sleep(1.5)

print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {failed} failed")
