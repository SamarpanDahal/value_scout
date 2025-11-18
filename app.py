from flask import Flask, request,redirect, jsonify, send_from_directory,flash, session
import requests
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#  Secret key for sessions
app.secret_key = "thisismysecretkeyforsessions"  

# SerpApi key
SERPAPI_KEY = "9c9ebdb9f7851dff0077e2ca096e4b82023ddbbb7b63fa5264ecaa0550ccdab5"

#database connection
from mysql.connector import pooling

# ✅ Connection Pool Configuration
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "value_scout"
}

# ✅ Create a pool of reusable connections
connection_pool = pooling.MySQLConnectionPool(
    pool_name="valueScoutPool",
    pool_size=10,                # up to 10 parallel connections
    pool_reset_session=True,
    **dbconfig
)

# ✅ Helper to get connection + cursor for each route
def get_db_cursor():
    """Fetch a connection and dictionary cursor from the pool."""
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    return conn, cursor
 

# Serve the login page as root
@app.route("/")
def login_page():
    if "loggedin" in session:
        return redirect("/frontend")
    return send_from_directory(os.path.dirname(__file__), "login.html")


#Register a user 

# GET request → serve registration page
@app.route("/register-page")
def register_page():
    return send_from_directory(os.path.dirname(__file__), "register.html")


# POST request → handle registration form
@app.route("/register", methods=["POST"])
def register():
    data = request.form
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return "Please fill all fields", 400

    hashed_password = generate_password_hash(password)

    conn = cursor = None
    try:
        conn, cursor = get_db_cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        return redirect("/")
    except mysql.connector.IntegrityError:
        return "Email already registered!", 400
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass

    

# User login
@app.route("/login", methods=["POST"])
def login():
    data = request.form
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return "Please fill all fields", 400
    conn, cursor = get_db_cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return "Email not registered!", 400

    # Compare password hashes
    if check_password_hash(user["password_hash"], password):
        #  Create session with actual user info
        session["loggedin"] = True
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["email"] = user["email"]

        session["just_logged_in"] = True 

        flash(f"Welcome, {user['username']}!", "success")
        return redirect("/frontend")
    else:
        return "Incorrect password!", 400

   # To ensure welcome message displayes once 
@app.route("/welcome_status")
def welcome_status():
    if session.get("just_logged_in"):
        session.pop("just_logged_in")  
        return jsonify({"show_welcome": True, "username": session.get("username")})
    return jsonify({"show_welcome": False})


    
#Frontend of website
@app.route("/frontend")
def frontend():
    if "loggedin" not in session:
        return redirect("/")
    return send_from_directory(os.path.dirname(__file__), "frontend.html")

# Display username when user login and session starts
@app.route("/get_username")
def get_username():
    if "loggedin" in session:
        return jsonify({"username": session["username"]})
    return jsonify({"username": None})




# ✅ Route to add wishlist item
@app.route("/add_to_wishlist", methods=["POST"])
def add_to_wishlist():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    user_id = session["user_id"]
    asin = data.get("asin")
    title = data.get("title")

    if not title:
        return jsonify({"error": "Missing title"}), 400

    conn = cursor = None
    try:
        conn, cursor = get_db_cursor()

        cursor.execute("SELECT * FROM wishlist WHERE user_id = %s AND asin = %s", (user_id, asin))
        existing = cursor.fetchone()

        if existing:
            # remove from wishlist
            cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND asin = %s", (user_id, asin))
            # also remove any tracking for this item
            if asin:
                cursor.execute("DELETE FROM wishlist_tracking WHERE user_id = %s AND asin = %s", (user_id, asin))
            else:
                cursor.execute("DELETE FROM wishlist_tracking WHERE user_id = %s AND title = %s", (user_id, title))
            conn.commit()
            return jsonify({"message": "Removed from wishlist", "status": "removed"}), 200
        else:
            # add
            cursor.execute("""
                INSERT INTO wishlist (user_id, asin, title, link, price, thumbnail, rating, reviews, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                asin,
                title,
                data.get("link"),
                data.get("price"),
                data.get("thumbnail"),
                data.get("rating"),
                data.get("reviews"),
                data.get("source"),
            ))
            conn.commit()
            return jsonify({"message": "Added to wishlist", "status": "added"}), 200

    except Exception as e:
        print("⚠️ Error in /add_to_wishlist:", e)
        return jsonify({"error": "Database error"}), 500
    finally:
        try:
            if cursor: cursor.close()
            if conn: conn.close()
        except:
            pass



# Wishlist page route
@app.route("/wishlist")
def wishlist_page():
    if "loggedin" not in session:
        return redirect("/")
    return send_from_directory(os.path.dirname(__file__), "wishlist.html")


@app.route("/wishlist_data")
def wishlist_data():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session["user_id"]

    try:
        # ✅ Get a pooled connection and cursor
        conn, cursor = get_db_cursor()

        cursor.execute("SELECT * FROM wishlist WHERE user_id = %s", (user_id,))
        items = cursor.fetchall()
        return jsonify(items)

    except Exception as e:
        print("⚠️ Error in /wishlist_data:", e)
        return jsonify({"error": "Database query failed"}), 500

    finally:
        # ✅ Always close cursor and connection
        try:
            cursor.close()
            conn.close()
        except:
            pass

@app.route("/remove_from_wishlist", methods=["POST"])
def remove_from_wishlist():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    asin = data.get("asin")
    title = data.get("title")
    user_id = session["user_id"]

    try:
        # ✅ Get pooled connection and cursor
        conn, cursor = get_db_cursor()

        if asin:
            # --- Delete using ASIN ---
            cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND asin = %s", (user_id, asin))
            cursor.execute("DELETE FROM wishlist_tracking WHERE user_id = %s AND asin = %s", (user_id, asin))
        else:
            # --- Fallback for older entries without ASIN ---
            cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND title = %s", (user_id, title))
            cursor.execute("DELETE FROM wishlist_tracking WHERE user_id = %s AND title = %s", (user_id, title))

        # ✅ Commit both deletes together
        conn.commit()

        return jsonify({"message": "Item removed and tracking cleared"}), 200

    except Exception as e:
        print("⚠️ Error in /remove_from_wishlist:", e)
        return jsonify({"error": "Database operation failed"}), 500

    finally:
        # ✅ Always close resources
        try:
            cursor.close()
            conn.close()
        except:
            pass




# Get tracked items
@app.route("/wishlist_tracking", methods=["GET"])
def get_tracking():
    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]

    try:
        
        conn, cursor = get_db_cursor()

        cursor.execute("SELECT * FROM wishlist_tracking WHERE user_id = %s", (user_id,))
        tracks = cursor.fetchall()
        return jsonify(tracks)

    except Exception as e:
        print("⚠️ Error in /wishlist_tracking:", e)
        return jsonify({"error": "Database query failed"}), 500

    finally:
       
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Add or update tracking
@app.route("/track_wishlist_item", methods=["POST"])
def track_wishlist_item():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    asin = data.get("asin")
    title = data.get("title")
    target_price = data.get("target_price")
    user_id = session["user_id"]

    try:
        # ✅ Get a pooled DB connection
        conn, cursor = get_db_cursor()

        # Check if already tracked
        cursor.execute("SELECT * FROM wishlist_tracking WHERE user_id = %s AND asin = %s", (user_id, asin))
        existing = cursor.fetchone()

        if existing:
            # --- Remove existing tracking ---
            cursor.execute("DELETE FROM wishlist_tracking WHERE user_id = %s AND asin = %s", (user_id, asin))
            conn.commit()
            return jsonify({"status": "removed"}), 200
        else:
            # --- Add new tracking ---
            cursor.execute("""
                INSERT INTO wishlist_tracking (user_id, asin, title, target_price)
                VALUES (%s, %s, %s, %s)
            """, (user_id, asin, title, target_price))
            conn.commit()
            return jsonify({"status": "added"}), 200

    except Exception as e:
        print("⚠️ Error in /track_wishlist_item:", e)
        return jsonify({"error": "Database operation failed"}), 500

    finally:
        # ✅ Close cursor and connection safely
        try:
            cursor.close()
            conn.close()
        except:
            pass


    

# ===============================
# 📦 CRON & NOTIFICATION ENDPOINTS
# ===============================

@app.route("/api/get_tracked_items")
def api_get_tracked_items():
    """Used by cron job to fetch all tracked wishlist items."""
    try:
        conn, cursor = get_db_cursor()

        cursor.execute("""
            SELECT wt.*, w.asin, w.link, w.thumbnail, u.email
            FROM wishlist_tracking wt
            JOIN users u ON wt.user_id = u.id
            JOIN wishlist w ON wt.user_id = w.user_id AND wt.asin = w.asin
        """)
        items = cursor.fetchall()
        return jsonify(items)

    except Exception as e:
        print("⚠️ Error in /api/get_tracked_items:", e)
        return jsonify({"error": "Failed to fetch tracked items"}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@app.route("/api/add_notification", methods=["POST"])
def api_add_notification():
    """Called by the cron when a price drop is detected."""
    try:
        conn, cursor = get_db_cursor()

        data = request.get_json()

        cursor.execute("""
            INSERT INTO notifications (user_id, asin, title, current_price, target_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["user_id"],
            data["asin"],            
            data["title"],
            data["current_price"],
            data["target_price"]
        ))
        conn.commit()
        return jsonify({"message": "Notification added"}), 200

    except Exception as e:
        print("⚠️ Error in /api/add_notification:", e)
        return jsonify({"error": "Failed to insert notification"}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass



@app.route("/api/get_notifications")
def get_notifications():
    """Fetch unread notifications for the logged-in user."""
    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]

    try:
        conn, cursor = get_db_cursor()

        cursor.execute("""
            SELECT * FROM notifications 
            WHERE user_id = %s AND is_read = FALSE 
            ORDER BY created_at DESC
        """, (user_id,))
        notifications = cursor.fetchall()
        return jsonify(notifications)

    except Exception as e:
        print("⚠️ Error in /api/get_notifications:", e)
        return jsonify({"error": "Failed to fetch notifications"}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@app.route("/api/mark_notification_read", methods=["POST"])
def mark_notification_read():
    """Mark a notification as read when the user acknowledges it."""
    try:
        conn, cursor = get_db_cursor()

        data = request.get_json()
        notif_id = data.get("id")

        cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s", (notif_id,))
        conn.commit()
        return jsonify({"message": "Notification marked as read"}), 200

    except Exception as e:
        print("⚠️ Error in /api/mark_notification_read:", e)
        return jsonify({"error": "Failed to mark notification as read"}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

@app.route("/api/check_existing_notification")
def check_existing_notification():
    user_id = request.args.get("user_id")
    asin = request.args.get("asin")

    try:
        conn, cursor = get_db_cursor()
        cursor.execute("""
            SELECT current_price 
            FROM notifications
            WHERE user_id = %s AND asin = %s AND is_read = FALSE
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id, asin))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return jsonify({
                "exists": True,
                "last_price": float(row["current_price"])
            })
        return jsonify({"exists": False})

    except Exception as e:
        print("Error in check_existing_notification:", e)
        return jsonify({"exists": False})







# Amazon product search route
@app.route("/search", methods=["GET"])
def search_amazon():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    url = "https://serpapi.com/search"
    params = {
        "engine": "amazon",
        "api_key": SERPAPI_KEY,
        "amazon_domain": "amazon.in",
        "k": query
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
    except Exception as e:
        return jsonify({"error": f"Error fetching Amazon results: {str(e)}"}), 500

    results = []
    for item in data.get("organic_results", [])[:20]:
        link = item.get("link", "")
        price_data = item.get("price")
        price = price_data.get("raw") if isinstance(price_data, dict) else price_data

        # ✅ Extract ASIN from link (unique product ID)
        asin = None
        if "/dp/" in link:
            try:
                asin = link.split("/dp/")[1].split("/")[0].split("?")[0]
            except Exception:
                asin = None

        results.append({
            "asin": asin,
            "title": item.get("title"),
            "link": link,
            "price": price,
            "thumbnail": item.get("thumbnail"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews"),
            "source": "Amazon"
        })

    return jsonify(results)



# Flipkart search route via Google Shopping
@app.route("/flipkart", methods=["GET"])
def search_flipkart():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "api_key": SERPAPI_KEY,
        "q": query,
        "google_domain": "google.co.in",
        "hl": "en",
        "gl": "in"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        print("Flipkart raw response:", response.text[:1000])  # Print first 1000 characters


        if "application/json" not in response.headers.get("Content-Type", ""):
            return jsonify({"error": "Invalid response format from SerpApi"}), 500

        data = response.json()
    except Exception as e:
        return jsonify({"error": f"Error fetching Flipkart results: {str(e)}"}), 500

    results = []
    for item in data.get("shopping_results", [])[:20]:
     
    # if "flipkart.com" in link:
     results.append({
    "title": item.get("title"),
    "link": item.get("product_link"),
    "price": item.get("price"),
    "thumbnail": item.get("thumbnail") or "",
    "rating": item.get("rating") or "N/A",
    "reviews": item.get("reviews") or "N/A",
    "source": item.get("source") or "Google Shopping"
})


    print("Filtered Flipkart products:", len(results))  # Confirm count
    return jsonify(results)








if __name__ == "__main__":
    app.run(debug=True, port=5000)
