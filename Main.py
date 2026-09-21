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
    "dyson",
    "roborock",
    "roomba"
]


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )


seen = set()

if os.path.exists("seen.txt"):
    with open("seen.txt", "r", encoding="utf-8") as f:
        seen = set(line.strip() for line in f if line.strip())

r = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

soup = BeautifulSoup(r.text, "html.parser")

script = soup.find(
    "script",
    {"id": "seoStructuredData"}
)

if not script:
    raise Exception("seoStructuredData not found")

data = json.loads(script.text)
items = data["mainEntity"]["itemListElement"]

for item in items:

    product = item.get("item", {})

    title = product.get("name", "")
    description = product.get("description", "")
    link = product.get("url", "")

    if not link:
        continue

    text_to_search = f"{title} {description}".lower()

    if not any(keyword in text_to_search for keyword in KEYWORDS):
        continue

    if link in seen:
        continue

    send_message(
        f"🔔 Novi oglas za usisivač\n\n"
        f"{title}\n\n"
        f"{link}"
    )

    seen.add(link)

with open("seen.txt", "w", encoding="utf-8") as f:
    for link in seen:
        f.write(link + "\n")
