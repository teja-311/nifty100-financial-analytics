import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = "output"
REPORT_DIR = "reports"

class CompanyClustering:

    def __init__(self):

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(REPORT_DIR, exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH)

        self.ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

    def prepare_data(self):

        latest = (
            self.ratios
            .assign(
                year_num=self.ratios["year"]
                .str.extract(r"(\d{4})")
                .astype(float)
            )
            .sort_values("year_num")
            .groupby("company_id")
            .tail(1)
            .reset_index(drop=True)
        )

        feature_columns = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "free_cash_flow_cr",
        "operating_profit_margin_pct"
        ]

        df = latest[["company_id"] + feature_columns].copy()

        return df

    def preprocess(self):

        df = self.prepare_data()
    
        df["return_on_equity_pct"] = df["return_on_equity_pct"].clip(-100, 100)
        df["operating_profit_margin_pct"] = df["operating_profit_margin_pct"].clip(-100, 100)

        feature_columns = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "free_cash_flow_cr",
        "operating_profit_margin_pct"
        ]

        # NOTE:
        # Sprint specification requires sector-wise median imputation.
        # The provided database schema does not contain sector information,
        # therefore overall median imputation is used instead.

        imputer = SimpleImputer(strategy="median")

        X = imputer.fit_transform(df[feature_columns])

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(X)

        return df, X_scaled

    def plot_elbow(self, X_scaled):

        inertia = []

        k_values = range(2, 11)

        for k in k_values:

            model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            model.fit(X_scaled)

            inertia.append(model.inertia_)

        plt.figure(figsize=(8,5))

        plt.plot(
            k_values,
            inertia,
            marker="o"
        )

        plt.title("Elbow Method")

        plt.xlabel("Number of Clusters")

        plt.ylabel("Inertia")

        plt.grid(True)

        plt.savefig(
            os.path.join(
                REPORT_DIR,
                "elbow_plot.png"
            )
        )

        plt.close()

    def run_kmeans(self):

        df, X_scaled = self.preprocess()

        self.plot_elbow(X_scaled)

        model = KMeans(
            n_clusters=5,
            random_state=42,
            n_init=10
        )

        clusters = model.fit_predict(X_scaled)
        temp = df.copy()
        temp["cluster_id"] = clusters

        print(
            temp.groupby("cluster_id")[
                [
                    "return_on_equity_pct",
                    "debt_to_equity",
                    "revenue_cagr_5yr",
                    "free_cash_flow_cr",
                    "operating_profit_margin_pct"
                ]
            ].mean().round(2)
        )

        distances = np.linalg.norm(
            X_scaled - model.cluster_centers_[clusters],
            axis=1
        )

        cluster_names = {
            0: "Stable Compounders",
            1: "High Return Leaders",
            2: "Balanced Growth",
            3: "Turnaround Candidates",
            4: "Aggressive Growth"
        }

        output = pd.DataFrame({

            "company_id": df["company_id"],

            "cluster_id": clusters,

            "cluster_name": [
                cluster_names[c]
                for c in clusters
            ],

            "distance_from_centroid": distances.round(4)

        })

        output.to_csv(
            os.path.join(
                OUTPUT_DIR,
                "cluster_labels.csv"
            ),
            index=False
        )

        print(output.head())

        print()

        print("Saved:")
        print("output/cluster_labels.csv")
        print("reports/elbow_plot.png")

if __name__ == "__main__":

    cluster = CompanyClustering()

    cluster.run_kmeans()
