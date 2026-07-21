import sqlite3
import pandas as pd
import os

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

violations = []
for table in tables:

    df = pd.read_sql_query(
        f"SELECT company_id FROM {table}",
        conn
    )

    invalid_ids = sorted(set(df["company_id"]) - company_ids)
    for invalid_id in invalid_ids:
        violations.append({
            "dq_rule": "DQ-03",
            "severity": "CRITICAL",
            "table_name": table,
            "invalid_company_id": invalid_id
        })

conn.close()

report_df = pd.DataFrame(violations)

os.makedirs("output", exist_ok=True)

report_df.to_csv(
    "output/fk_validation_report.csv",
    index=False
)

print(report_df)
print("\nfk_validation_report.csv created successfully!")