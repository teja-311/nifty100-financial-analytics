import os
from pydoc import text
import re
import pandas as pd

INPUT_FILE = "data/raw/analysis.xlsx"

OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


class AnalysisParser:

    def __init__(self):

        self.df = pd.read_excel(
            INPUT_FILE,
            header=1
        )

        self.pattern = re.compile(
            r"(\d+)\s*Years?:?\s*(-?[\d.]+)%"
        )

        self.records = []

        self.failures = []

        self.metrics = [

            "compounded_sales_growth",

            "compounded_profit_growth",

            "stock_price_cagr",

            "roe"

        ]
    
    ########################################################
    # Parse Analysis Fields
    ########################################################

    def parse(self):

        for _, row in self.df.iterrows():

            company = row["company_id"]

            for metric in self.metrics:

                value = row.get(metric)

                if pd.isna(value):

                    continue

                text = str(value).strip()

                # Handle TTM
                if text.startswith("TTM"):
                    ttm_match = re.search(r"(-?[\d.]+)%", text)

                    if ttm_match:
                        self.records.append({
                            "company_id": company,
                            "metric_type": metric,
                            "period_years": 0,
                            "value_pct": float(ttm_match.group(1))
                        })
                        continue

                # Handle Last Year
                if text.startswith("Last Year"):
                    last_match = re.search(r"(-?[\d.]+)%", text)

                    if last_match:
                        self.records.append({
                            "company_id": company,
                            "metric_type": metric,
                            "period_years": 1,
                            "value_pct": float(last_match.group(1))
                        })
                        continue

                match = self.pattern.search(text)

                if match:

                    self.records.append({

                        "company_id": company,

                        "metric_type": metric,

                        "period_years": int(match.group(1)),

                        "value_pct": float(match.group(2))

                    })

                else:

                    self.failures.append({

                        "company_id": company,

                        "metric_type": metric,

                        "raw_text": text

                    })
    
    ########################################################
    # Export Results
    ########################################################

    def export(self):

        parsed_df = pd.DataFrame(self.records)

        failures_df = pd.DataFrame(self.failures)

        parsed_df.to_csv(
            "output/analysis_parsed.csv",
            index=False
        )

        failures_df.to_csv(
            "output/parse_failures.csv",
            index=False
        )

        print("\nParsing Completed")
        print(f"Records Parsed   : {len(parsed_df)}")
        print(f"Parse Failures   : {len(failures_df)}")
        print("\nSaved:")
        print(" - output/analysis_parsed.csv")
        print(" - output/parse_failures.csv")
    
def main():

    print("=" * 60)
    print("Analysis Parser")
    print("=" * 60)

    parser = AnalysisParser()

    parser.parse()

    parser.export()

    print("\nSprint 5 - Day 29 Completed")


if __name__ == "__main__":
    main()