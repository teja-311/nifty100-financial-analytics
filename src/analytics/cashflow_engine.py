import sqlite3
import pandas as pd
import os

from src.analytics.cashflow_kpis import *

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

cashflow = pd.read_sql_query(
"""
SELECT *
FROM cashflow
""",
conn
)

profit = pd.read_sql_query(
"""
SELECT
company_id,
year,
sales,
operating_profit,
net_profit
FROM profitandloss
""",
conn
)

conn.close()

df = cashflow.merge(
    profit,
    on=["company_id","year"],
    how="left"
)

records = []

for _, row in df.iterrows():

    cfo = row["operating_activity"]
    cfi = row["investing_activity"]
    cff = row["financing_activity"]

    fcf = free_cash_flow(cfo, cfi)

    quality = cfo_quality_score(
        cfo,
        row["net_profit"]
    )

    capex = capex_intensity(
        cfi,
        row["sales"]
    )

    conversion = fcf_conversion_rate(
        fcf,
        row["operating_profit"]
    )

    pattern = capital_allocation_pattern(
        cfo,
        cfi,
        cff,
        quality
    )

    records.append({

        "company_id":row["company_id"],

        "year":row["year"],

        "free_cash_flow":fcf,

        "cfo_quality":quality,

        "capex_intensity":capex,

        "fcf_conversion_rate":conversion,

        "capital_pattern":pattern

    })

result = pd.DataFrame(records)

os.makedirs(
    "output",
    exist_ok=True
)

result.to_csv(
    "output/capital_allocation.csv",
    index=False
)

print(result.head())

print()

print("Rows:",len(result))

print()

print("capital_allocation.csv created.")