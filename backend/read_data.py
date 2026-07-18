import pandas as pd

# Read the CSV file into something Python can work with (called a "DataFrame")
df = pd.read_csv("../data/sales_data.csv")

# Show the first 5 rows, just to prove we can see it
print("=== First 5 rows ===")
print(df.head())

# Show basic info: column names, data types, how many rows
print("\n=== Data summary ===")
print(df.info())

# Show a quick total
print("\n=== Total sales amount ===")
print(df["TotalAmount"].sum())
