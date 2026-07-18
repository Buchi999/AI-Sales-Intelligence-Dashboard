import sqlite3
import pandas as pd

conn = sqlite3.connect("../database/sales_intel.db")

# Pull the sales table straight out of the database into a Python table
sales = pd.read_sql_query("SELECT * FROM sales", conn)

print("=== Top Customers by Total Spending ===")
top_customers = sales.groupby("CustomerName")["TotalAmount"].sum().sort_values(ascending=False)
print(top_customers)

print("\n=== Best-Selling Products (by revenue) ===")
top_products = sales.groupby("Product")["TotalAmount"].sum().sort_values(ascending=False)
print(top_products)

print("\n=== Revenue by Region ===")
by_region = sales.groupby("Region")["TotalAmount"].sum().sort_values(ascending=False)
print(by_region)

print("\n=== Most Popular Payment Method ===")
by_payment = sales["PaymentMethod"].value_counts()
print(by_payment)

conn.close()
