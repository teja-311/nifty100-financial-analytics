import sqlite3
import pandas as pd
import os

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

# Load Profit & Loss table
pl = pd.read_sql_query("""
SELECT
    company_id,
    year,
    sales,
    operating_profit,
    opm_percentage
FROM profitandloss
""", conn)

# Load sector information
sectors = pd.read_sql_query("""
SELECT
    company_id,
    broad_sector
FROM sectors
""", conn)

conn.close()

# Merge sector information
pl = pl.merge(
    sectors,
    on="company_id",
    how="left"
)

mismatches = []

for _, row in pl.iterrows():

    sales = row["sales"]
    operating_profit = row["operating_profit"]
    source_opm = row["opm_percentage"]

    # Skip incomplete records
    if pd.isna(sales) or pd.isna(operating_profit) or pd.isna(source_opm):
        continue

    if sales == 0:
        continue

    calculated_opm = round(
        (operating_profit / sales) * 100,
        2
    )

    difference = abs(calculated_opm - source_opm)

    if difference > 1:

        sector = row["broad_sector"]

        if sector == "Financials":
            remark = "Financial sector - review separately"
        else:
            remark = "OPM mismatch"

        mismatches.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "sector": sector,
            "source_opm": source_opm,
            "calculated_opm": calculated_opm,
            "difference": round(difference, 2),
            "remark": remark
        })

os.makedirs("output", exist_ok=True)

report = pd.DataFrame(mismatches)

report.to_csv(
    "output/opm_crosscheck.csv",
    index=False
)

print(report.head())

print("\nSummary")

print(report["remark"].value_counts())

print(f"\nTotal mismatches: {len(report)}")

print("\nopm_crosscheck.csv updated successfully!")