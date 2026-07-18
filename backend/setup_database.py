import pandas as pd
import sqlite3

# Read our CSV data
df = pd.read_csv("../data/sales_data.csv")

# Connect to (or create) the database file
conn = sqlite3.connect("../database/sales_intel.db")

# Build the "customers" table: one row per unique person
customers = df[["CustomerName", "CustomerEmail", "Region"]].drop_duplicates()
customers.to_sql("customers", conn, if_exists="replace", index=False)

# Build the "sales" table: every transaction, as-is
df.to_sql("sales", conn, if_exists="replace", index=False)

conn.close()
print("Database created successfully at database/sales_intel.db")
