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

✅ VALUE SCOUT — QUICK SETUP GUIDE (For Demo Laptop)
1. Install Software

Install Python 3

Install MySQL Server + Workbench

MySQL password must be: root

2. Set Up Database

Open MySQL Workbench

Login (user: root, pass: root)

Create DB:

CREATE DATABASE value_scout;


Import the file: value_scout.sql into this database

3. Set Up the Project

Download project folder (from GitHub/ZIP)

Open terminal inside the project folder

Install dependencies:

pip install -r requirements.txt

4. Run the Website

Inside project folder:

python app.py


Open browser:

http://127.0.0.1:5000

5. Run the Price Tracker

Open a second terminal:

python price_tracker_cron.py


This will check prices and send email alerts.

🎉 DONE
Done!
