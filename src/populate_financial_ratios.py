import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

# Load existing financial ratios table
financial = pd.read_sql_query(
    "SELECT * FROM financial_ratios",
    conn
)

# Load CAGR results
cagr = pd.read_csv("output/cagr_results.csv")

# Merge
financial = financial.merge(
    cagr,
    on="company_id",
    how="left"
)

# Replace table
financial.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

count = pd.read_sql_query(
    "SELECT COUNT(*) AS rows FROM financial_ratios",
    conn
)

print(count)

conn.close()

print("\nfinancial_ratios updated successfully.")