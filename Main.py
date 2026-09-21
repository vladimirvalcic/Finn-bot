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
    "roomba",
    "miele",
    "electrolux",
    "bosch",
    "philips",
]


def send_message(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print("TELEGRAM:", r.status_code)


print("BOT STARTED")

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

print("STATUS:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

script = soup.find(
    "script",
    {"id": "seoStructuredData"}
)

if not script:
    print("seoStructuredData not found")
    exit()

data = json.loads(script.text)
items = data["mainEntity"]["itemListElement"]

print("ITEMS FOUND:", len(items))

for item in items:

    product = item.get("item", {})

    title = product.get("name", "")
    description = product.get("description", "")
    link = product.get("url", "")

    text_to_search = f"{title} {description}".lower()

    print("CHECKING:", title)

    if not any(keyword in text_to_search for keyword in KEYWORDS):
        continue

    print("MATCH:", title)

    if link in seen:
        continue

    send_message(
        f"🔔 Novi usisivač!\n\n"
        f"{title}\n\n"
        f"{description}\n\n"
        f"{link}"
    )

    seen.add(link)

with open("seen.txt", "w", encoding="utf-8") as f:
    for link in seen:
        f.write(link + "\n")

print("BOT FINISHED")
