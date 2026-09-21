import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://www.finn.no/recommerce/forsale/search?location=1.20003.20046&location=1.20003.20045&location=1.20007.20110&location=0.20061&sort=PRICE_ASC"

KEYWORDS = [
    "støvsuger",
    "robotstøvsuger",
    "dyson"
]


def send_message(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print("TELEGRAM STATUS:", r.status_code)
    print("TELEGRAM RESPONSE:", r.text)


print("BOT STARTED")

seen = set()

if os.path.exists("seen.txt"):
    with open("seen.txt", "r", encoding="utf-8") as f:
        seen = set(line.strip() for line in f if line.strip())

print("SEEN ITEMS:", len(seen))

r = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    },
    timeout=30
)

print("STATUS:", r.status_code)
print("PAGE SIZE:", len(r.text))

soup = BeautifulSoup(r.text, "html.parser")

script = soup.find(
    "script",
    {"id": "seoStructuredData"}
)

print("SEO SCRIPT FOUND:", script is not None)

if script is None:
    print("ERROR: seoStructuredData NOT FOUND")
    exit()

try:
    data = json.loads(script.text)
    items = data["mainEntity"]["itemListElement"]

    print("ITEMS FOUND:", len(items))

    for item in items:
        product = item["item"]

        title = product.get("name", "")
        link = product.get("url", "")

        print("CHECKING:", title)

        if not link:
            continue

        title_lower = title.lower()

        if not any(word in title_lower for word in KEYWORDS):
            continue

        print("KEYWORD MATCH:", title)

        if link in seen:
            print("ALREADY SEEN")
            continue

        print("NEW ITEM FOUND:", title)

        send_message(
            f"🔔 Novi usisivač!\n\n{title}\n\n{link}"
        )

        seen.add(link)

except Exception as e:
    print("ERROR:", str(e))

with open("seen.txt", "w", encoding="utf-8") as f:
    for link in seen:
        f.write(link + "\n")

print("BOT FINISHED")
