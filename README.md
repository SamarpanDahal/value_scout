# value_scout
Price tracking website with wishlist + email alerts.

📘 ValueScout — Price Tracking Website

ValueScout is a Python Flask-based price tracker that:

✔ Searches Amazon & Flipkart
✔ Lets users add items to wishlist
✔ Tracks price changes using cron script
✔ Sends automatic email alerts
✔ Shows notifications inside the website
🚀 How to Run

1️⃣ Install dependencies:
pip install -r requirements.txt

2️⃣ Import Database

Use MySQL Workbench → Server → Data Import
Import value_scout.sql

3️⃣ Run the server:
python app.py

4️⃣ Run the price tracker:
python price_tracker_cron.py


Done!
