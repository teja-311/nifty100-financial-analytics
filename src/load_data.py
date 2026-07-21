import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"
conn = sqlite3.connect(DB_PATH)

files = {
    "analysis": ("data/raw/analysis.xlsx", 1),
    "balancesheet": ("data/raw/balancesheet.xlsx", 1),
    "cashflow": ("data/raw/cashflow.xlsx", 1),
    "companies": ("data/raw/companies.xlsx", 1),
    "documents": ("data/raw/documents.xlsx", 1),
    "financial_ratios": ("data/raw/financial_ratios.xlsx", 0),
    "market_cap": ("data/raw/market_cap.xlsx", 0),
    "peer_groups": ("data/raw/peer_groups.xlsx", 0),
    "profitandloss": ("data/raw/profitandloss.xlsx", 1),
    "sectors": ("data/raw/sectors.xlsx", 0),
    "stock_prices": ("data/raw/stock_prices.xlsx", 0)
}

for table, (file, header_row) in files.items():

    print(f"\nLoading {table}...")
    df = pd.read_excel(file, header=header_row)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df.to_sql(
        table,
        conn,
        if_exists="replace",
        index=False
    )

    print(f"{len(df)} rows loaded")

conn.close()
print("\nAll tables loaded successfully!")