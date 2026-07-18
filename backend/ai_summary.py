import sqlite3
import pandas as pd
import os
from groq import Groq

# Get the API key from the environment variable we set earlier
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found. Did you run the export command?")
    exit()

client = Groq(api_key=api_key)

conn = sqlite3.connect("../database/sales_intel.db")
sales = pd.read_sql_query("SELECT * FROM sales", conn)
conn.close()

# Build the same pattern data we calculated before
top_customers = sales.groupby("CustomerName")["TotalAmount"].sum().sort_values(ascending=False)
top_products = sales.groupby("Product")["TotalAmount"].sum().sort_values(ascending=False)
by_region = sales.groupby("Region")["TotalAmount"].sum().sort_values(ascending=False)
total_revenue = sales["TotalAmount"].sum()

# Turn those numbers into plain text, to hand to the AI as context
summary_data = f"""
Total revenue: {total_revenue}
Top customers by spending: {top_customers.to_dict()}
Best-selling products by revenue: {top_products.to_dict()}
Revenue by region: {by_region.to_dict()}
"""

# Ask the AI to write a plain-English business summary
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a business analyst. Write a short, clear, plain-English summary of sales data for a small business owner. Avoid jargon. 3-4 sentences max."},
        {"role": "user", "content": summary_data}
    ]
)

print("=== AI-Generated Business Summary ===")
print(response.choices[0].message.content)
