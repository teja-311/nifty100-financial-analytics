import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = "db/nifty100.db"


class ValuationEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.load_data()

    def load_data(self):

        self.market = pd.read_sql("""

            SELECT *

            FROM market_cap

        """, self.conn)

        self.ratios = pd.read_sql("""

            SELECT *

            FROM financial_ratios

        """, self.conn)

        self.sectors = pd.read_sql("""

            SELECT *

            FROM sectors

        """, self.conn)

        self.companies = pd.read_sql("""

            SELECT *

            FROM companies

        """, self.conn)

        latest_market = (

            self.market

            .sort_values("year")

            .groupby("company_id")

            .last()

            .reset_index()

        )

        latest_ratios = (

            self.ratios

            .sort_values("year")

            .groupby("company_id")

            .last()

            .reset_index()

        )

        self.df = (

            latest_market

            .merge(

                latest_ratios,

                on="company_id",

                how="left",

                suffixes=("_market","")

            )

            .merge(

                self.sectors,

                on="company_id",

                how="left"

            )

            .merge(

                self.companies,

                left_on="company_id",

                right_on="id",

                how="left",

                suffixes=("","_company")

            )

        )

        ########################################################
    # Calculate Valuation Metrics
    ########################################################

    def calculate(self):

        self.df["fcf_yield_pct"] = (

            self.df["free_cash_flow_cr"]

            / self.df["market_cap_crore"]

            * 100

        ).round(2)

        sector_median = (

            self.df

            .groupby("broad_sector")["pe_ratio"]

            .median()

            .reset_index()

            .rename(

                columns={

                    "pe_ratio": "sector_median_pe"

                }

            )

        )

        self.df = self.df.merge(

            sector_median,

            on="broad_sector",

            how="left"

        )

        self.df["pe_vs_sector_pct"] = (

            self.df["pe_ratio"]

            / self.df["sector_median_pe"]

            * 100

        ).round(2)

        conditions = [

            self.df["pe_ratio"]

            > self.df["sector_median_pe"] * 1.5,

            self.df["pe_ratio"]

            < self.df["sector_median_pe"] * 0.7

        ]

        choices = [

            "Caution",

            "Discount"

        ]

        self.df["valuation_flag"] = np.select(

            conditions,

            choices,

            default="Fair"

        )

        self.output = self.df[[

            "company_id",

            "company_name",

            "broad_sector",

            "market_cap_crore",

            "pe_ratio",

            "pb_ratio",

            "ev_ebitda",

            "free_cash_flow_cr",

            "fcf_yield_pct",

            "sector_median_pe",

            "pe_vs_sector_pct",

            "valuation_flag"

        ]]

        ########################################################
    # Export Reports
    ########################################################

    def export(self):

        os.makedirs("output", exist_ok=True)

        self.output.to_excel(
            "output/valuation_summary.xlsx",
            index=False
        )

        self.output.to_csv(
            "output/valuation_flags.csv",
            index=False
        )

        print("\nValuation reports generated successfully.")
        print("Saved:")
        print(" - output/valuation_summary.xlsx")
        print(" - output/valuation_flags.csv")

def main():

    print("=" * 60)
    print("Valuation Engine")
    print("=" * 60)

    engine = ValuationEngine()

    print("Calculating valuation metrics...")
    engine.calculate()

    print("Exporting reports...")
    engine.export()

    engine.conn.close()

    print("\nSprint 4 - Valuation Module Completed")


if __name__ == "__main__":
    main()       