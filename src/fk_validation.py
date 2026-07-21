import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql_query(
    "SELECT id FROM companies",
    conn
)

company_ids = set(companies["id"])
tables = [
    "analysis",
    "balancesheet",
    "cashflow",
    "documents",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "profitandloss",
    "sectors",
    "stock_prices"
]

print("=" * 60)
print("FOREIGN KEY VALIDATION")
print("=" * 60)
total_violations = 0

for table in tables:
    df = pd.read_sql_query(
        f"SELECT company_id FROM {table}",
        conn
    )

    invalid = set(df["company_id"]) - company_ids

    if len(invalid) == 0:
        print(f"{table:<20} PASS")
    else:
        print(f"{table:<20} FAIL ({len(invalid)} invalid company_id values)")
        print("Invalid IDs:", sorted(invalid))
        total_violations += len(invalid)

print("\n" + "=" * 60)
print(f"Total FK Violations: {total_violations}")

if total_violations == 0:
    print("Foreign Key Validation: PASS")
else:
    print("Foreign Key Validation: FAIL")

conn.close()