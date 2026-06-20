import pandas as pd
import sqlite3

# Load cleaned/original datasets
providers = pd.read_csv("providers_data.csv")
receivers = pd.read_csv("receivers_data.csv")
food_listings = pd.read_csv("food_listings_cleaned.csv")
claims = pd.read_csv("claims_cleaned.csv")

# Connect to (or create) the SQLite database file
conn = sqlite3.connect("food_wastage.db")

# Push each DataFrame into a SQL table
providers.to_sql("providers", conn, if_exists="replace", index=False)
receivers.to_sql("receivers", conn, if_exists="replace", index=False)
food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
claims.to_sql("claims", conn, if_exists="replace", index=False)

print("Database created successfully: food_wastage.db")

# Quick check: list all tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Quick check: row counts
for table in ["providers", "receivers", "food_listings", "claims"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} rows")

conn.close()