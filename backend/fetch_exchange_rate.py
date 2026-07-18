import requests
import sqlite3
from datetime import datetime, timezone

def get_exchange_rate(base="USD"):
    url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(url)
    return response.json()

def save_rate_to_db(rate, base, target):
    conn = sqlite3.connect("../database/sales_intel.db")
    cursor = conn.cursor()

    # Create the table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT,
            target_currency TEXT,
            rate REAL,
            fetched_at TEXT
        )
    """)

    # Insert this new reading
    cursor.execute("""
        INSERT INTO exchange_rates (base_currency, target_currency, rate, fetched_at)
        VALUES (?, ?, ?, ?)
    """, (base, target, rate, datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    result = get_exchange_rate("USD")

    if result.get("result") == "success":
        rate = result["rates"]["NGN"]
        print(f"1 USD = {rate} NGN today ({result['time_last_update_utc']})")
        save_rate_to_db(rate, "USD", "NGN")
        print("Saved to database.")
    else:
        print("Something went wrong:")
        print(result)
