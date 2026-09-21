import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# TEST TELEGRAMA
test = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": "✅ TEST PORUKA IZ FINN BOTA"
    }
)

print("TEST STATUS:", test.status_code)
print("TEST RESPONSE:", test.text)

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
    "philips"
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

r = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

print("STATUS:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

script = soup.find("script", {"id": "seoStructuredData"})

print("SEO SCRIPT FOUND:", script is not None)

if not script:
    raise Exception("seoStructuredData not found")

data = json.loads(script.text)
items = data["mainEntity"]["itemListElement"]

print("ITEMS FOUND:", len(items))

for item in items:
    product = item.get("item", {})

    title = product.get("name", "")
    description = product.get("description", "")
    link = product.get("url", "")

    text_to_search = f"{title} {description}".lower()

    for keyword in KEYWORDS:
        if keyword in text_to_search:
            send_message(
                f"🔔 Novi usisivač!\n\n{title}\n\n{description}\n\n{link}"
            )
            break

print("BOT FINISHED")
