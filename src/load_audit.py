import sqlite3
import pandas as pd
import os

DB_PATH = "db/nifty100.db"
conn = sqlite3.connect(DB_PATH)

tables = [
    "analysis",
    "balancesheet",
    "cashflow",
    "companies",
    "documents",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "profitandloss",
    "sectors",
    "stock_prices"
]

audit = []

for table in tables:
    count = pd.read_sql_query(
        f"SELECT COUNT(*) AS row_count FROM {table}",
        conn
    )["row_count"][0]

    audit.append({
        "table_name": table,
        "row_count": count,
        "rejected_rows": 0
    })

conn.close()

audit_df = pd.DataFrame(audit)
os.makedirs("output", exist_ok=True)
audit_df.to_csv("output/load_audit.csv", index=False)
print(audit_df)
print("\nload_audit.csv created successfully!")