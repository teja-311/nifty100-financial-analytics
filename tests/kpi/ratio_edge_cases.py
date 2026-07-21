import pandas as pd
import os

df = pd.read_csv("output/cagr_results.csv")

os.makedirs("output", exist_ok=True)

with open("output/ratio_edge_cases.log", "w") as f:

    for _, row in df.iterrows():

        for col in df.columns:

            if "flag" in col:

                value = row[col]

                if value != "OK":

                    f.write(
                        f"{row['company_id']} | {col} | {value}\n"
                    )

print("ratio_edge_cases.log created.")