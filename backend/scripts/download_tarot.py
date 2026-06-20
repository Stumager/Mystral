import os
import time

import requests

BASE = "https://upload.wikimedia.org/wikipedia/commons"
CARDS = {
    0:  "/9/90/RWS_Tarot_00_Fool.jpg",
    1:  "/d/de/RWS_Tarot_01_Magician.jpg",
    2:  "/8/88/RWS_Tarot_02_High_Priestess.jpg",
    3:  "/d/d2/RWS_Tarot_03_Empress.jpg",
    4:  "/c/c3/RWS_Tarot_04_Emperor.jpg",
    5:  "/8/8d/RWS_Tarot_05_Hierophant.jpg",
    6:  "/d/db/RWS_Tarot_06_Lovers.jpg",
    7:  "/9/9b/RWS_Tarot_07_Chariot.jpg",
    8:  "/f/f5/RWS_Tarot_08_Strength.jpg",
    9:  "/4/4d/RWS_Tarot_09_Hermit.jpg",
    10: "/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    11: "/e/e0/RWS_Tarot_11_Justice.jpg",
    12: "/2/2b/RWS_Tarot_12_Hanged_Man.jpg",
    13: "/d/d7/RWS_Tarot_13_Death.jpg",
    14: "/f/f8/RWS_Tarot_14_Temperance.jpg",
    15: "/5/55/RWS_Tarot_15_Devil.jpg",
    16: "/5/53/RWS_Tarot_16_Tower.jpg",
    17: "/d/db/RWS_Tarot_17_Star.jpg",
    18: "/7/7f/RWS_Tarot_18_Moon.jpg",
    19: "/1/17/RWS_Tarot_19_Sun.jpg",
    20: "/d/dd/RWS_Tarot_20_Judgement.jpg",
    21: "/f/ff/RWS_Tarot_21_World.jpg",
}

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "tarot")
os.makedirs(OUT_DIR, exist_ok=True)

for card_id, path in CARDS.items():
    url = BASE + path
    filename = os.path.join(OUT_DIR, f"{card_id}.jpg")
    if os.path.exists(filename):
        print(f"  {card_id} (exists)")
        continue
    r = requests.get(url, headers={"User-Agent": "Mystral/1.0"}, timeout=15)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"OK {card_id}")
    else:
        print(f"FAIL {card_id}: {r.status_code}")
    time.sleep(2)

print("Done")
