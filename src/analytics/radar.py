import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

DB_PATH = "db/nifty100.db"


class RadarChartGenerator:

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

        self.financial = (
            self.financial
            .sort_values("year")
            .groupby("company_id")
            .last()
            .reset_index()
        )

        self.companies = pd.read_sql("""
        SELECT *
        FROM companies
        """, self.conn)

        self.df = (
            self.peer
            .merge(
                self.financial,
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

        self.metrics = [

            "return_on_equity_pct",

            "net_profit_margin_pct",

            "debt_to_equity",

            "free_cash_flow_cr",

            "pat_cagr_5yr",

            "revenue_cagr_5yr",

            "asset_turnover"

        ]

    ###########################################################

    def create_chart(self, company_row, peer_group):

        peer_df = self.df[
            self.df["peer_group_name"] == peer_group
        ]

        peer_avg = []

        company_values = []

        labels = []

        for metric in self.metrics:

            if metric not in peer_df.columns:
                continue

            labels.append(metric)

            peer_avg.append(
                peer_df[metric]
                .fillna(0)
                .mean()
            )

            company_values.append(
                company_row.get(metric,0)
            )

        N = len(labels)

        angles = np.linspace(
            0,
            2*np.pi,
            N,
            endpoint=False
        )

        angles = np.concatenate(
            (angles,[angles[0]])
        )

        company_values.append(
            company_values[0]
        )

        peer_avg.append(
            peer_avg[0]
        )

        fig = plt.figure(
            figsize=(6,6)
        )

        ax = plt.subplot(
            polar=True
        )

        ax.plot(
            angles,
            company_values,
            linewidth=2
        )

        ax.fill(
            angles,
            company_values,
            alpha=0.25
        )

        ax.plot(
            angles,
            peer_avg,
            linestyle="--"
        )

        ax.set_xticks(
            angles[:-1]
        )

        ax.set_xticklabels(
            labels,
            fontsize=8
        )

        plt.title(
            company_row["company_id"]
        )

        os.makedirs(
            "reports/radar_charts",
            exist_ok=True
        )

        filename = os.path.join(
            "reports/radar_charts",
            f"{company_row['company_id']}_radar.png"
        )

        plt.savefig(
            filename,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

###########################################################

def main():

    engine = RadarChartGenerator()

    print("=" * 60)
    print("Generating Radar Charts")
    print("=" * 60)

    total = 0

    processed = set()

    for _, row in engine.df.iterrows():

        company = row["company_id"]

        if company in processed:
            continue

        processed.add(company)

        peer_group = row["peer_group_name"]

        if pd.isna(peer_group):
            continue

        try:

            engine.create_chart(
                row,
                peer_group
            )

            total += 1

            if total % 10 == 0:
                print(f"{total} charts generated...")

        except Exception:

            continue

    engine.conn.close()

    print()

    print("=" * 60)
    print("Radar Charts Completed")
    print("=" * 60)

    print()

    print(f"Charts Generated : {total}")

    print("Saved to:")

    print("reports/radar_charts/")


###########################################################

if __name__ == "__main__":

    main()