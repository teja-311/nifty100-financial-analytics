import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = "db/nifty100.db"


class PeerEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.load_data()

    def load_data(self):

        self.peer = pd.read_sql("""
            SELECT *
            FROM peer_groups
        """, self.conn)

        self.financial = pd.read_sql("""
            SELECT *
            FROM financial_ratios
        """, self.conn)

        self.market = pd.read_sql("""
            SELECT *
            FROM market_cap
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

        self.df = (
            self.peer
            .merge(
                self.financial,
                on="company_id",
                how="left"
            )
            .merge(
                latest_market,
                on="company_id",
                how="left",
                suffixes=("", "_market")
            )
            .merge(
                self.companies,
                left_on="company_id",
                right_on="id",
                how="left",
                suffixes=("", "_company")
            )
        )

        self.df = self.df.drop_duplicates()

    ########################################################
    # Percentile Ranking
    ########################################################

    def percentile_rank(self, group, column, inverse=False):

        if column not in group.columns:

            return pd.Series(
                [np.nan] * len(group),
                index=group.index
            )

        values = group[column].fillna(0)

        rank = values.rank(
            pct=True,
            method="average"
        )

        if inverse:
            rank = 1 - rank

        return (rank * 100).round(2)

    ########################################################
    # Compute Rankings
    ########################################################

    def compute(self):

        results = []

        metrics = {

            "return_on_equity_pct": False,

            "net_profit_margin_pct": False,

            "debt_to_equity": True,

            "free_cash_flow_cr": False,

            "revenue_cagr_5yr": False,

            "pat_cagr_5yr": False,

            "eps_cagr_5yr": False,

            "interest_coverage": False,

            "asset_turnover": False,

            "market_cap_crore": False

        }

        for peer_group, group in self.df.groupby("peer_group_name"):

            temp = group.copy()

            for metric, inverse in metrics.items():

                temp[f"{metric}_percentile"] = self.percentile_rank(
                    temp,
                    metric,
                    inverse
                )

            results.append(temp)

        self.result = pd.concat(
            results,
            ignore_index=True
        )

    ########################################################
    # SQLite Export
    ########################################################

    def save_sqlite(self):

        export = []

        metrics = [

            "return_on_equity_pct",

            "net_profit_margin_pct",

            "debt_to_equity",

            "free_cash_flow_cr",

            "revenue_cagr_5yr",

            "pat_cagr_5yr",

            "eps_cagr_5yr",

            "interest_coverage",

            "asset_turnover",

            "market_cap_crore"

        ]

        for _, row in self.result.iterrows():

            latest_year = row["year"]

            for metric in metrics:

                export.append({

                    "company_id":
                        row["company_id"],

                    "peer_group_name":
                        row["peer_group_name"],

                    "metric":
                        metric,

                    "value":
                        row.get(metric),

                    "percentile_rank":
                        row.get(
                            f"{metric}_percentile"
                        ),

                    "year":
                        latest_year

                })

        export = pd.DataFrame(export)

        export.to_sql(

            "peer_percentiles",

            self.conn,

            if_exists="replace",

            index=False

        )

        print()

        print("SQLite table created:")

        print("peer_percentiles")

    ########################################################
    # Excel Export
    ########################################################

    def export_excel(self):

        os.makedirs(

            "output",

            exist_ok=True

        )

        writer = pd.ExcelWriter(

            "output/peer_comparison.xlsx",

            engine="openpyxl"

        )

        for peer_group, group in self.result.groupby(

            "peer_group_name"

        ):

            group.to_excel(

                writer,

                sheet_name=peer_group[:31],

                index=False

            )

        writer.close()

        print()

        print("=" * 60)

        print("Peer Comparison Report Generated")

        print("=" * 60)

        print()

        print("Saved:")
        print("output/peer_comparison.xlsx")

########################################################
# Main
########################################################

def main():

    engine = PeerEngine()

    print()

    print("=" * 60)
    print("Computing Peer Percentiles...")
    print("=" * 60)

    engine.compute()

    print("Done.")

    print()

    print("=" * 60)
    print("Saving SQLite...")
    print("=" * 60)

    engine.save_sqlite()

    print()

    print("=" * 60)
    print("Generating Excel...")
    print("=" * 60)

    engine.export_excel()

    engine.conn.close()

    print()

    print("=" * 60)
    print("Sprint 3 - Peer Engine Completed")
    print("=" * 60)


if __name__ == "__main__":

    main() 