import re
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE_URL = "http://127.0.0.1:5000"
SERPAPI_KEY = "9c9ebdb9f7851dff0077e2ca096e4b82023ddbbb7b63fa5264ecaa0550ccdab5"


# ============================
# 1️⃣ Get Tracked Items (API)
# ============================
def fetch_tracked_items():
    try:
        res = requests.get(f"{BASE_URL}/api/get_tracked_items")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Failed to fetch tracked items:", e)
        return []


# ============================
# 2️⃣ Price Check (SerpApi + HTML)
# ============================
def check_price_on_amazon(asin):
    """Try SerpApi first → If fails, fallback to HTML scraping."""

    # ---------- SerpApi Search ----------
    try:
        params = {
            "engine": "amazon",
            "api_key": SERPAPI_KEY,
            "amazon_domain": "amazon.in",
            "k": asin
        }
        res = requests.get("https://serpapi.com/search", params=params)
        data = res.json()

        for item in data.get("organic_results", []):
            link = item.get("link", "")
            if f"/dp/{asin}" not in link:
                continue

            price_data = item.get("price")
            price_str = price_data.get("raw") if isinstance(price_data, dict) else price_data

            if price_str:
                price_num = re.sub(r"[^\d.]", "", price_str)
                if price_num:
                    price = float(price_num)
                    print(f"✅ SerpApi found match for {asin}: ₹{price}")
                    return price

        print(f"⚠️ SerpApi returned no price for ASIN {asin}, using fallback...")

    except Exception as e:
        print("⚠️ SerpApi error:", e)

    # ---------- Fallback: BeautifulSoup ----------
    try:
        print(f"🕵️ Scraping Amazon page for ASIN {asin}...")
        url = f"https://www.amazon.in/dp/{asin}"
        headers = {"User-Agent": "Mozilla/5.0"}

        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        selectors = [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".a-price .a-offscreen"
        ]

        for sel in selectors:
            tag = soup.select_one(sel)
            if tag:
                price_text = re.sub(r"[^\d.]", "", tag.text)
                if price_text:
                    price = float(price_text)
                    print(f"✅ Fallback HTML price found: ₹{price}")
                    return price

    except Exception as e:
        print("❌ Fallback HTML error:", e)

    print(f"❌ Could not fetch price for ASIN {asin}")
    return None


# ============================
# 3️⃣ Add Notification to DB
# ============================
def notify_backend(user_id, asin, title, current_price, target_price):
    """
    Prevent duplicate notifications:
    - If unread notification exists AND price is same → skip
    - If price is lower → insert new notification
    """
    try:
        # Check previous notification
        res = requests.get(f"{BASE_URL}/api/check_existing_notification", params={
            "user_id": user_id,
            "asin": asin
        })

        data = res.json()
        exists = data.get("exists", False)
        last_price = data.get("last_price")

        if exists:
            # If previous unread notification AND same price → skip
            if last_price == current_price:
                print(f"⚠ Already notified earlier (same price ₹{current_price}). Skipping…")
                return False

            # If price dropped further → send new notification
            if current_price < last_price:
                print(f"🔻 Price dropped further ({last_price} → {current_price}). Updating notification…")

        # Insert new notification
        payload = {
            "user_id": user_id,
            "asin": asin,
            "title": title,
            "current_price": current_price,
            "target_price": target_price
        }
        res = requests.post(f"{BASE_URL}/api/add_notification", json=payload)

        if res.status_code == 200:
            print(f"📌 New notification inserted for '{title}' @ ₹{current_price}")
            return True

        print("❌ Failed to insert notification.")
        return False

    except Exception as e:
        print("❌ notify_backend error:", e)
        return False




# ============================
# 4️⃣ Send Combined Email
# ============================
def send_combined_email(user_email, dropped_items):
    sender_email = "valuescout6@gmail.com"
    sender_password = "odpf qvdg ulle iism"   # ← replace with app password

    subject = f"🔥 {len(dropped_items)} Price Drop Alert(s)! — ValueScout"

    html_items = ""
    for item in dropped_items:
        html_items += f"""
        <div style="margin-bottom:16px;">
            <img src="{item['thumbnail']}" width="140" style="border-radius:8px;"><br><br>
            <b>{item['title']}</b><br>
            <b>Current Price:</b> ₹{item['current_price']}<br>
            <b>Your Target:</b> ₹{item['target_price']}<br><br>
            <a href="{item['link']}">View Product</a>
        </div>
        <hr>
        """

    html_body = f"""
    <h2>📉 Price Drop Alert</h2>
    <p>The following items dropped in price:</p>
    {html_items}
    <p style="margin-top:20px;">Happy shopping! 🛍️</p>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())

        print(f"📧 Email sent → {user_email} ({len(dropped_items)} items)")

    except Exception as e:
        print("❌ Email sending error:", e)


# ============================
# 5️⃣ MAIN PRICE TRACKER LOOP
# ============================
def run_price_check():
    items = fetch_tracked_items()
    print(f"\n📦 Tracked items fetched: {len(items)}\n")

    # store results grouped by user
    batch_emails = {}

    for item in items:
        asin = item["asin"]
        title = item["title"]
        target_price = float(item["target_price"])
        user_id = item["user_id"]
        user_email = item["email"]

        print(f"🔍 Checking '{title}' (ASIN {asin}, target ₹{target_price})...")

        price = check_price_on_amazon(asin)
        if price is None:
            print("❌ Price not found.\n")
            continue

        print(f"   💰 Current Price: ₹{price}")

        if price <= target_price:
            print(f"   🎯 Price Drop! (₹{price} ≤ ₹{target_price})")
            # Save to DB (only if not already notified)
            notified = notify_backend(user_id, asin, title, price, target_price)
            
            # Only if inserted successfully → add to email batch
            if notified:
                if user_email not in batch_emails:
                    batch_emails[user_email] = []
            
                batch_emails[user_email].append({
                    "title": title,
                    "asin": asin,
                    "current_price": price,
                    "target_price": target_price,
                    "thumbnail": item.get("thumbnail"),
                    "link": item["link"]
                })
            



        print("-" * 55)

    # 📧 Send ONE combined email to each user
    for email, drops in batch_emails.items():
        send_combined_email(email, drops)

    print("\n✅ Price check completed.\n📊 Emails sent:", len(batch_emails))


# ============================
# 6️⃣ Run Program
# ============================
if __name__ == "__main__":
    print("🚀 Starting ValueScout Price Tracker...\n")
    run_price_check()
    print("\n🎉 Finished execution.\n")
