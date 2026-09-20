import requests
import json
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8767742995:AAGG0w-kRiTMRLgrIfmyDoujQY9VYGxSJio"
CHAT_ID = "8996107100"

URL = "https://www.finn.no/recommerce/forsale/search?location=1.20003.20046&location=1.20003.20045&location=1.20007.20110&location=0.20061&sort=PRICE_ASC"

KEYWORDS = [
    "støvsuger",
    "robotstøvsuger",
    "dyson"
]

seen = set()


def send_message(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )

        if r.status_code == 200:
            print("✅ Poslata notifikacija")
        else:
            print("❌ Telegram greška:", r.text)

    except Exception as e:
        print("❌ Telegram greška:", e)


print("🔎 Pratim FINN...")

first_run = True

while True:
    try:
        r = requests.get(
            URL,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=20
        )

        soup = BeautifulSoup(r.text, "html.parser")

        script = soup.find(
            "script",
            {"id": "seoStructuredData"}
        )

        if not script:
            time.sleep(15)
            continue

        data = json.loads(script.text)

        items = data["mainEntity"]["itemListElement"]

        # Pri prvom pokretanju samo zapamti oglase
        if first_run:
            for item in items:
                product = item["item"]
                seen.add(product.get("url", ""))

            first_run = False
            print(f"✅ Zapamćeno {len(seen)} postojećih oglasa")
            time.sleep(15)
            continue

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

            seen.add(link)

            msg = (
                f"🔔 Novi usisivač pronađen!\n\n"
                f"{title}\n\n"
                f"{link}"
            )

            print(msg)

            send_message(msg)

        time.sleep(15)

    except Exception as e:
        print("Greška:", e)
        time.sleep(15)
