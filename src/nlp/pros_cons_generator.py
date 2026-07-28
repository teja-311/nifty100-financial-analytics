import os
import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


class ProsConsGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.pros_cons = []

        self.analysis = pd.read_csv(
            "output/analysis_parsed.csv"
        )

        self.ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        self.companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )

        self.balance = pd.read_sql(
            "SELECT * FROM balancesheet",
            self.conn
        )

        self.pnl = pd.read_sql(
            "SELECT * FROM profitandloss",
            self.conn
        )

        ##################################################
    # Helpers
    ##################################################

    def latest(self, company):

        df = self.ratios[
            self.ratios.company_id == company
        ].copy()

        if df.empty:
            return None

        df["year_num"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
            .astype(int)
        )

        return df.sort_values("year_num").iloc[-1]


    def history(self, company):

        df = self.ratios[
            self.ratios.company_id == company
        ].copy()

        if df.empty:
            return df

        df["year_num"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
        )

        # Treat TTM as the latest period
        df.loc[
            df["year"].astype(str).str.upper() == "TTM",
            "year_num"
        ] = 9999

        df["year_num"] = pd.to_numeric(
            df["year_num"],
            errors="coerce"
        )

        # Drop rows where year_num is null
        df = df.dropna(subset=["year_num"])

        df["year_num"] = df["year_num"].astype(int)

        return df.sort_values("year_num")


    def balance_history(self, company):

        df = self.balance[
            self.balance.company_id == company
        ].copy()

        if df.empty:
            return df

        df["year_num"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
        )

        # Treat TTM as the latest period
        df.loc[
            df["year"].astype(str).str.upper() == "TTM",
            "year_num"
        ] = 9999

        df["year_num"] = pd.to_numeric(
            df["year_num"],
            errors="coerce"
        )

        df = df.dropna(subset=["year_num"])

        df["year_num"] = df["year_num"].astype(int)

        return df.sort_values("year_num")


    def pnl_history(self, company):

        df = self.pnl[
            self.pnl.company_id == company
        ].copy()

        if df.empty:
            return df

        df["year_num"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
        )

        # Treat TTM as the latest period
        df.loc[
            df["year"].astype(str).str.upper() == "TTM",
            "year_num"
        ] = 9999

        df["year_num"] = pd.to_numeric(
            df["year_num"],
            errors="coerce"
        )

        df = df.dropna(subset=["year_num"])

        df["year_num"] = df["year_num"].astype(int)

        return df.sort_values("year_num")


    def add_record(
        self,
        company,
        rule_id,
        text,
        confidence,
        record_type
    ):

        if confidence < 60:
            return

        self.pros_cons.append({

            "company_id": company,

            "type": record_type,

            "rule_id": rule_id,

            "text": text,

            "confidence_pct": confidence

        })

        ##################################################
    # Pro Rules
    ##################################################

    def generate_pros(self):

        for company in self.companies["id"]:

            latest = self.latest(company)

            history = self.history(company)

            if latest is None:
                continue

            # -----------------------------
            # Pro Rule 1
            # ROE > 20% for 3+ years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                if (last3["return_on_equity_pct"] > 20).all():

                    self.add_record(
                        company,
                        "PRO_01",
                        "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
                        95,
                        "pro"
                    )

            # -----------------------------
            # Pro Rule 2
            # FCF positive for 5 years
            # -----------------------------
            if len(history) >= 5:

                last5 = history.tail(5)

                if (last5["free_cash_flow_cr"] > 0).all():

                    self.add_record(
                        company,
                        "PRO_02",
                        "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
                        90,
                        "pro"
                    )

            # -----------------------------
            # Pro Rule 3
            # Debt Free
            # -----------------------------
            if latest["debt_to_equity"] == 0:

                self.add_record(
                    company,
                    "PRO_03",
                    "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
                    100,
                    "pro"
                )

            # -----------------------------
            # Pro Rule 4
            # Revenue CAGR >15%
            # -----------------------------
            if latest["revenue_cagr_5yr"] > 15:

                self.add_record(
                    company,
                    "PRO_04",
                    "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum.",
                    85,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 5
            # OPM > 25%
            # -----------------------------
            if latest["operating_profit_margin_pct"] > 25:

                self.add_record(
                    company,
                    "PRO_05",
                    "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
                    90,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 6
            # PAT CAGR > 20%
            # -----------------------------
            if latest["pat_cagr_5yr"] > 20:

                self.add_record(
                    company,
                    "PRO_06",
                    "Net profit compounding at above 20% over 5 years creates significant shareholder value.",
                    90,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 7
            # Interest Coverage > 10
            # OR Debt Free
            # -----------------------------
            if (
                latest["interest_coverage"] > 10
                or latest["debt_to_equity"] == 0
            ):

                self.add_record(
                    company,
                    "PRO_07",
                    "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
                    85,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 8
            # Dividend payout + Positive FCF
            # -----------------------------
            if (
                latest["dividend_payout_ratio_pct"] > 20
                and latest["free_cash_flow_cr"] > 0
            ):

                self.add_record(
                    company,
                    "PRO_08",
                    "Consistent dividend payouts backed by positive free cash flow indicate healthy shareholder returns.",
                    80,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 9
            # EPS CAGR > 15%
            # -----------------------------
            if latest["eps_cagr_5yr"] > 15:

                self.add_record(
                    company,
                    "PRO_09",
                    "Earnings per share growing above 15% CAGR over 5 years indicates strong profitability growth.",
                    90,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 10
            # ROE improving for 3 years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                roe = last3["return_on_equity_pct"].tolist()

                if roe[0] < roe[1] < roe[2]:

                    self.add_record(
                        company,
                        "PRO_10",
                        "Return on equity has improved consistently over the last three years.",
                        85,
                        "pro"
                    )

                        # -----------------------------
            # Pro Rule 11
            # Revenue CAGR > PAT CAGR
            # -----------------------------
            if latest["revenue_cagr_5yr"] > latest["pat_cagr_5yr"]:

                self.add_record(
                    company,
                    "PRO_11",
                    "Revenue growth is outpacing profit growth, indicating strong business expansion.",
                    80,
                    "pro"
                )

                        # -----------------------------
            # Pro Rule 12
            # Assets growing & Borrowings declining
            # -----------------------------
            balance = self.balance_history(company)

            if len(balance) >= 3:

                last3 = balance.tail(3)

                assets = last3["total_assets"].tolist()
                debt = last3["borrowings"].tolist()

                if (
                    assets[0] < assets[1] < assets[2]
                    and
                    debt[0] > debt[1] > debt[2]
                ):

                    self.add_record(
                        company,
                        "PRO_12",
                        "Total assets have consistently increased while borrowings have declined over the last three years.",
                        90,
                        "pro"
                    )

    ##################################################
    # Con Rules
    ##################################################

    def generate_cons(self):

        for company in self.companies["id"]:

            latest = self.latest(company)

            history = self.history(company)

            if latest is None:
                continue

            # -----------------------------
            # Con Rule 1
            # Debt to Equity > 2
            # -----------------------------
            if latest["debt_to_equity"] > 2:

                self.add_record(
                    company,
                    "CON_01",
                    f"Debt-to-equity ratio of {latest['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring.",
                    90,
                    "con"
                )

            # -----------------------------
            # Con Rule 2
            # FCF negative for 3 years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                if (last3["free_cash_flow_cr"] < 0).all():

                    self.add_record(
                        company,
                        "CON_02",
                        "Free cash flow negative for 3 consecutive years raises concern about cash generation quality.",
                        90,
                        "con"
                    )

            # -----------------------------
            # Con Rule 3
            # OPM declining for 3 years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                opm = last3["operating_profit_margin_pct"].tolist()

                if opm[0] > opm[1] > opm[2]:

                    self.add_record(
                        company,
                        "CON_03",
                        "Operating margins declining for 3 consecutive years suggest pricing or cost pressure.",
                        85,
                        "con"
                    )

            # -----------------------------
            # Con Rule 4
            # Net Profit Margin negative
            # -----------------------------
            if latest["net_profit_margin_pct"] < 0:

                self.add_record(
                    company,
                    "CON_04",
                    "Company reported a net loss in the most recent financial year.",
                    95,
                    "con"
                )

                        # -----------------------------
            # Con Rule 5
            # Revenue CAGR < 5%
            # -----------------------------
            if latest["revenue_cagr_5yr"] < 5:

                self.add_record(
                    company,
                    "CON_05",
                    "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum.",
                    85,
                    "con"
                )

                        # -----------------------------
            # Con Rule 6
            # Interest Coverage < 1.5
            # -----------------------------
            if latest["interest_coverage"] < 1.5:

                self.add_record(
                    company,
                    "CON_06",
                    "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations.",
                    95,
                    "con"
                )

                        # -----------------------------
            # Con Rule 7
            # Dividend payout >100%
            # -----------------------------
            if latest["dividend_payout_ratio_pct"] > 100:

                self.add_record(
                    company,
                    "CON_07",
                    "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable.",
                    90,
                    "con"
                )

                        # -----------------------------
            # Con Rule 8
            # Debt rising for 3 years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                debt = last3["debt_to_equity"].tolist()

                if debt[0] < debt[1] < debt[2]:

                    self.add_record(
                        company,
                        "CON_08",
                        "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk.",
                        85,
                        "con"
                    )

                        # -----------------------------
            # Con Rule 9
            # EPS declining for 3 years
            # -----------------------------
            if len(history) >= 3:

                last3 = history.tail(3)

                eps = last3["earnings_per_share"].tolist()

                if eps[0] > eps[1] > eps[2]:

                    self.add_record(
                        company,
                        "CON_09",
                        "Earnings per share have declined for three consecutive years.",
                        90,
                        "con"
                    )

                        # -----------------------------
            # Con Rule 10
            # ROE below 10% (adapted from ROCE)
            # -----------------------------
            if latest["return_on_equity_pct"] < 10:

                self.add_record(
                    company,
                    "CON_10",
                    "Return on equity below 10% indicates weak shareholder returns.",
                    85,
                    "con"
                )

                        # -----------------------------
            # Con Rule 11
            # Borrowings > 3x Operating Profit
            # (Adapted from Net Debt > 3x EBITDA)
            # -----------------------------
            pnl = self.pnl_history(company)

            balance = self.balance_history(company)

            if not pnl.empty and not balance.empty:

                latest_pnl = pnl.iloc[-1]
                latest_balance = balance.iloc[-1]

                if (
                    latest_pnl["operating_profit"] > 0
                    and
                    latest_balance["borrowings"] >
                    3 * latest_pnl["operating_profit"]
                ):

                    self.add_record(
                        company,
                        "CON_11",
                        "Borrowings are more than three times the latest operating profit, indicating elevated leverage.",
                        90,
                        "con"
                    )

    def run(self):

        self.generate_pros()
        self.generate_cons()

        df = pd.DataFrame(self.pros_cons)
        # -------------------------------------------------
        # Ensure every company has at least one Pro and Con
        # -------------------------------------------------

        pro_companies = set(
            df[df["type"] == "pro"]["company_id"]
        )

        con_companies = set(
            df[df["type"] == "con"]["company_id"]
        )

        for company in self.companies["id"]:

            if company not in pro_companies:

                self.pros_cons.append({

                    "company_id": company,
                    "type": "pro",
                    "rule_id": "PRO_DEFAULT",
                    "text": "Business demonstrates stable financial performance with no major strengths detected by the automated screening rules.",
                    "confidence_pct": 61

                })

            if company not in con_companies:

                self.pros_cons.append({

                    "company_id": company,
                    "type": "con",
                    "rule_id": "CON_DEFAULT",
                    "text": "No significant financial weaknesses were detected by the automated screening rules.",
                    "confidence_pct": 61

                })

        df = pd.DataFrame(self.pros_cons)

        df.to_csv(
            "output/pros_cons_generated.csv",
            index=False
        )

        print(df.head(20))
        print()

        print("Total Generated :", len(df))
        print("Pros Generated  :", (df["type"] == "pro").sum())
        print("Cons Generated  :", (df["type"] == "con").sum())

        

def main():

    generator = ProsConsGenerator()

    generator.run()


if __name__ == "__main__":
    main()