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
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


seen = set()

if os.path.exists("seen.txt"):
    with open("seen.txt", "r", encoding="utf-8") as f:
        seen = set(line.strip() for line in f if line.strip())

r = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(r.text, "html.parser")

script = soup.find(
    "script",
    {"id": "seoStructuredData"}
)

data = json.loads(script.text)

items = data["mainEntity"]["itemListElement"]

for item in items:

    product = item["item"]

    title = product.get("name", "")
    link = product.get("url", "")

    if not link:
        continue

    title_lower = title.lower()

    if not any(word in title_lower for word in KEYWORDS):
        continue

    if link in seen:
        continue

    send_message(
        f"🔔 Novi usisivač!\n\n{title}\n\n{link}"
    )

    seen.add(link)

with open("seen.txt", "w", encoding="utf-8") as f:
    for link in seen:
        f.write(link + "\n")
