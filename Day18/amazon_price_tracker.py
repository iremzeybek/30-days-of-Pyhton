import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import matplotlib.pyplot as plt


# ----------------------------
# CONFIGURATION
# ----------------------------
PRODUCT_URL = "https://www.amazon.com/dp/B0CHX1W1XY"  
TARGET_PRICE = 150.00
CHECK_EVERY_SECONDS = 60  

CSV_FILE = Path("price_history.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


# ----------------------------
# FETCH PRODUCT PAGE
# ----------------------------
def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


# ----------------------------
# PARSE PRODUCT TITLE
# ----------------------------
def parse_title(soup):
    title_tag = soup.find(id="productTitle")
    if not title_tag:
        return "Unknown Product"
    return title_tag.get_text(strip=True)


# ----------------------------
# PARSE PRICE
# ----------------------------
def parse_price(soup):
    selectors = [
        "span.a-price span.a-offscreen",
        "span#priceblock_ourprice",
        "span#priceblock_dealprice",
        "span#price_inside_buybox"
    ]

    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(strip=True)
            cleaned = (
                text.replace("$", "")
                    .replace(",", "")
                    .strip()
            )
            try:
                return float(cleaned)
            except ValueError:
                continue

    return None


# ----------------------------
# GET PRODUCT DATA
# ----------------------------
def get_product_data():
    html = fetch_page(PRODUCT_URL)
    soup = BeautifulSoup(html, "html.parser")

    title = parse_title(soup)
    price = parse_price(soup)

    if price is None:
        raise ValueError("Could not find price on page.")

    return {
        "timestamp": datetime.now(),
        "title": title,
        "price": price
    }


# ----------------------------
# SAVE TO CSV
# ----------------------------
def save_record(record):
    df_new = pd.DataFrame([record])

    if CSV_FILE.exists():
        df_old = pd.read_csv(CSV_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(CSV_FILE, index=False)


# ----------------------------
# LOAD HISTORY
# ----------------------------
def load_history():
    if not CSV_FILE.exists():
        return pd.DataFrame(columns=["timestamp", "title", "price"])

    df = pd.read_csv(CSV_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ----------------------------
# PRICE ALERT
# ----------------------------
def check_alert(price):
    if price <= TARGET_PRICE:
        print("\\n🚨 PRICE ALERT!")
        print(f"Current price: ${price:.2f}")
        print(f"Target price:  ${TARGET_PRICE:.2f}\\n")


# ----------------------------
# SHOW PRICE STATS
# ----------------------------
def show_stats(df):
    if df.empty:
        return

    print("--- Price Statistics ---")
    print(f"Records:      {len(df)}")
    print(f"Lowest price: ${df['price'].min():.2f}")
    print(f"Highest price:${df['price'].max():.2f}")
    print(f"Average price:${df['price'].mean():.2f}")
    print()


# ----------------------------
# PLOT PRICE HISTORY
# ----------------------------
def plot_history(df):
    if len(df) < 2:
        print("Not enough data to plot yet.")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(df["timestamp"], df["price"], marker="o")
    plt.title("Amazon Price History")
    plt.xlabel("Time")
    plt.ylabel("Price ($)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


# ----------------------------
# MAIN MONITOR LOOP
# ----------------------------
def monitor():
    print("Starting Amazon price tracker...")
    print(f"Checking every {CHECK_EVERY_SECONDS} seconds\\n")

    previous_price = None

    while True:
        try:
            data = get_product_data()

            print(f"[{data['timestamp']:%Y-%m-%d %H:%M:%S}]")
            print(data["title"])
            print(f"Price: ${data['price']:.2f}")

            if previous_price is not None:
                diff = data["price"] - previous_price

                if diff < 0:
                    print(f"⬇ Price dropped by ${abs(diff):.2f}")
                elif diff > 0:
                    print(f"⬆ Price increased by ${diff:.2f}")
                else:
                    print("➖ Price unchanged")

            save_record(data)
            check_alert(data["price"])

            history = load_history()
            show_stats(history)

            previous_price = data["price"]

        except Exception as e:
            print(f"Error: {e}")

        print("-" * 50)
        time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    monitor()
