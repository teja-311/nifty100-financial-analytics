import os
import sqlite3
import pandas as pd

from cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_year(df):
    df = df.copy()

    df["year_num"] = pd.to_numeric(
        df["year"].astype(str).str.extract(r"(\d+)")[0],
        errors="coerce",
    )

    df = df.dropna(subset=["year_num"])

    df["year_num"] = df["year_num"].astype(int)

    return df


def latest_records(df):

    df = extract_year(df)

    return (
        df.sort_values("year_num")
        .groupby("company_id", as_index=False)
        .tail(1)
        .drop(columns="year_num")
    )


def prepare_previous_borrowings(balance):

    balance = extract_year(balance)

    balance = balance.sort_values(
        ["company_id", "year_num"]
    )

    balance["previous_borrowings"] = (
        balance.groupby("company_id")["borrowings"]
        .shift(1)
    )

    latest_balance = (
        balance.groupby("company_id", as_index=False)
        .tail(1)
    )

    return latest_balance[
        [
            "company_id",
            "borrowings",
            "previous_borrowings",
        ]
    ]


def calculate_fcf_cagr(df):

    df = extract_year(df)

    df = df.sort_values("year_num")

    df["fcf"] = (
        df["operating_activity"]
        +
        df["investing_activity"]
    )

    if len(df) < 5:
        return None

    start = df.iloc[0]["fcf"]
    end = df.iloc[-1]["fcf"]

    if start <= 0 or end <= 0:
        return None

    years = len(df) - 1

    return (
        (
            (end / start)
            ** (1 / years)
        )
        - 1
    ) * 100


def main():

    conn = sqlite3.connect(DB_PATH)

    cashflow = pd.read_sql(
        "SELECT * FROM cashflow",
        conn,
    )

    profit = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn,
    )

    balance = pd.read_sql(
        "SELECT * FROM balancesheet",
        conn,
    )

    conn.close()

    latest_balance = prepare_previous_borrowings(
        balance
    )

    results = []

    for company in cashflow["company_id"].unique():

        cf = cashflow[
            cashflow["company_id"] == company
        ].copy()

        pl = profit[
            profit["company_id"] == company
        ].copy()

        merged = cf.merge(
            pl[
                [
                    "company_id",
                    "year",
                    "sales",
                    "operating_profit",
                    "net_profit",
                ]
            ],
            on=["company_id", "year"],
            how="inner",
        )

        if merged.empty:
            continue

        merged = extract_year(merged)

        merged = merged.sort_values("year_num")

        latest = merged.iloc[-1]

        fcf = free_cash_flow(
            latest["operating_activity"],
            latest["investing_activity"],
        )

        merged["cfo_pat_ratio"] = (
            merged["operating_activity"]
            /
            merged["net_profit"].replace(
                0,
                pd.NA,
            )
        )

        avg_ratio = merged[
            "cfo_pat_ratio"
        ].mean()

        quality = cfo_quality_score(
            latest["operating_activity"],
            latest["net_profit"],
        )

        capex_pct = None

        if latest["sales"] != 0:

            capex_pct = (
                abs(
                    latest[
                        "investing_activity"
                    ]
                )
                /
                latest["sales"]
            ) * 100

        capex_label = capex_intensity(
            latest["investing_activity"],
            latest["sales"],
        )

        fcf_cagr = calculate_fcf_cagr(
            merged
        )

        conversion = (
            fcf_conversion_rate(
                fcf,
                latest[
                    "operating_profit"
                ],
            )
        )

        allocation = (
            capital_allocation_pattern(
                latest[
                    "operating_activity"
                ],
                latest[
                    "investing_activity"
                ],
                latest[
                    "financing_activity"
                ],
                quality,
            )
        )

        borrow = latest_balance[
            latest_balance[
                "company_id"
            ]
            == company
        ]

        if borrow.empty:
            previous_borrowings = None
            current_borrowings = None
        else:
            previous_borrowings = borrow.iloc[0]["previous_borrowings"]
            current_borrowings = borrow.iloc[0]["borrowings"]

        distress = (
            latest["operating_activity"] < 0
            and latest["financing_activity"] > 0
        )

        deleveraging = (
            pd.notna(previous_borrowings)
            and latest["financing_activity"] < 0
            and current_borrowings < previous_borrowings
        )

        results.append(
            {
                "company_id": company,
                "sector": "N/A",
                "cfo_quality_score": round(avg_ratio, 2)
                if pd.notna(avg_ratio)
                else None,
                "cfo_quality_label": quality,
                "capex_intensity_pct": round(capex_pct, 2)
                if capex_pct is not None
                else None,
                "capex_label": capex_label,
                "fcf_cagr_5yr": round(fcf_cagr, 2)
                if fcf_cagr is not None
                else None,
                "fcf_conversion_pct": conversion,
                "distress_flag": distress,
                "deleveraging_flag": deleveraging,
                "capital_allocation_label": allocation,
                "cfo_value": latest["operating_activity"],
                "cff_value": latest["financing_activity"],
                "latest_net_profit": latest["net_profit"],
            }
        )

    result = pd.DataFrame(results)

    result[
        [
            "company_id",
            "sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ]
    ].to_excel(
        os.path.join(
            OUTPUT_DIR,
            "cashflow_intelligence.xlsx",
        ),
        index=False,
    )

    result[
        result["distress_flag"]
    ][
        [
            "company_id",
            "cfo_value",
            "cff_value",
            "latest_net_profit",
        ]
    ].to_csv(
        os.path.join(
            OUTPUT_DIR,
            "distress_alerts.csv",
        ),
        index=False,
    )

    print("=" * 60)
    print("Cash Flow Intelligence Module Completed")
    print("=" * 60)
    print(f"Companies Processed : {len(result)}")
    print(f"Distress Companies  : {result['distress_flag'].sum()}")
    print(f"Deleveraging Firms  : {result['deleveraging_flag'].sum()}")
    print("Generated:")
    print("  - output/cashflow_intelligence.xlsx")
    print("  - output/distress_alerts.csv")


if __name__ == "__main__":
    main()