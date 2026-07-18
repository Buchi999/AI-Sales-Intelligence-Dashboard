import sqlite3
import pandas as pd

conn = sqlite3.connect("../database/sales_intel.db")
sales = pd.read_sql_query("SELECT * FROM sales", conn)

# Make sure "Date" is treated as an actual date, not just text
sales["Date"] = pd.to_datetime(sales["Date"])

# How many unique days do we have data for?
num_days = sales["Date"].nunique()

# Total revenue divided by number of days = average revenue per day
total_revenue = sales["TotalAmount"].sum()
avg_daily_revenue = total_revenue / num_days

# Simple projection: average day x 30 = a rough month
projected_month = avg_daily_revenue * 30

print(f"Data covers {num_days} days")
print(f"Total revenue so far: {total_revenue}")
print(f"Average revenue per day: {avg_daily_revenue:.2f}")
print(f"Rough projection for a 30-day month: {projected_month:.2f}")

conn.close()
