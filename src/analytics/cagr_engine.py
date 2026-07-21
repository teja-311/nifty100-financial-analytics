import sqlite3
import pandas as pd
import os
from src.analytics.cagr import calculate_cagr

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

pl = pd.read_sql_query("""
SELECT
    company_id,
    year,
    sales,
    net_profit,
    eps
FROM profitandloss
""", conn)

# Load master company list
companies_master = pd.read_sql_query("""
SELECT id
FROM companies
""", conn)

conn.close()

pl = pl[pl["year"] != "TTM"].copy()

pl["year_num"] = pl["year"].str.extract(r"(\d{4})").astype(int)

pl = pl.sort_values(
    by=["company_id", "year_num"]
)

def calculate_metric_cagr(company_df, metric_column, years=5):
    """
    Generic CAGR calculator for any metric.

    Parameters:
        company_df : DataFrame for one company
        metric_column : sales / net_profit / eps
        years : CAGR window

    Returns:
        (value, flag)
    """

    company_df = company_df.sort_values("year_num")

    if len(company_df) < years + 1:
        return None, "INSUFFICIENT"

    start = company_df.iloc[-(years + 1)]
    end = company_df.iloc[-1]

    start_value = start[metric_column]
    end_value = end[metric_column]

    actual_years = end["year_num"] - start["year_num"]

    return calculate_cagr(
        start_value,
        end_value,
        actual_years
    )

# -------------------------------------------------
# Revenue CAGR (5-Year) for all companies
# -------------------------------------------------

results = []

companies = sorted(companies_master["id"].tolist())

for company in companies:

    company_df = pl[
        pl["company_id"] == company
    ].copy()

    if company_df.empty:
        results.append({
            "company_id": company,
            "revenue_cagr_5yr": None,
            "revenue_flag": "NO_DATA",
            "pat_cagr_5yr": None,
            "pat_flag": "NO_DATA",
            "eps_cagr_5yr": None,
            "eps_flag": "NO_DATA"
        })
        continue

    # Revenue CAGR
    rev3, rev3_flag = calculate_metric_cagr(company_df, "sales", 3)
    rev5, rev5_flag = calculate_metric_cagr(company_df, "sales", 5)
    rev10, rev10_flag = calculate_metric_cagr(company_df, "sales", 10)

    # PAT CAGR
    pat3, pat3_flag = calculate_metric_cagr(company_df, "net_profit", 3)
    pat5, pat5_flag = calculate_metric_cagr(company_df, "net_profit", 5)
    pat10, pat10_flag = calculate_metric_cagr(company_df, "net_profit", 10)

    # EPS CAGR
    eps3, eps3_flag = calculate_metric_cagr(company_df, "eps", 3)
    eps5, eps5_flag = calculate_metric_cagr(company_df, "eps", 5)
    eps10, eps10_flag = calculate_metric_cagr(company_df, "eps", 10)

    results.append({

        "company_id": company,

        "revenue_cagr_3yr": rev3,
        "revenue_cagr_5yr": rev5,
        "revenue_cagr_10yr": rev10,

        "revenue_flag_3yr": rev3_flag,
        "revenue_flag_5yr": rev5_flag,
        "revenue_flag_10yr": rev10_flag,

        "pat_cagr_3yr": pat3,
        "pat_cagr_5yr": pat5,
        "pat_cagr_10yr": pat10,

        "pat_flag_3yr": pat3_flag,
        "pat_flag_5yr": pat5_flag,
        "pat_flag_10yr": pat10_flag,

        "eps_cagr_3yr": eps3,
        "eps_cagr_5yr": eps5,
        "eps_cagr_10yr": eps10,

        "eps_flag_3yr": eps3_flag,
        "eps_flag_5yr": eps5_flag,
        "eps_flag_10yr": eps10_flag

    })

results_df = pd.DataFrame(results)

print(results_df.head(10))

print("\nCompanies processed:", len(results_df))

os.makedirs("output", exist_ok=True)

results_df.to_csv(
    "output/cagr_results.csv",
    index=False
)

print("\nSaved output/cagr_results.csv")