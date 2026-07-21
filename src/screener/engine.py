from csv import writer
import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = "db/nifty100.db"


class ScreenerEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.load_data()

    def load_data(self):

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

        self.sectors = pd.read_sql("""
            SELECT *
            FROM sectors
        """, self.conn)

        self.df = (
            self.financial
            .merge(
                self.companies,
                left_on="company_id",
                right_on="id",
                how="left",
                suffixes=("", "_company")
            )
            .merge(
                self.sectors,
                left_on="company_id",
                right_on="company_id",
                how="left",
                suffixes=("", "_sector")
            )
        )

        # Latest market cap for each company
        latest_market = (
            self.market
            .sort_values("year")
            .groupby("company_id")
            .last()
            .reset_index()
        )

        self.df = self.df.merge(
            latest_market[
                [
            "company_id",
            "market_cap_crore",
            "enterprise_value_crore",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "dividend_yield_pct"
                ]
            ],
            on="company_id",
            how="left"
        )

        self.df = self.df.drop_duplicates()
            

    ######################################################
    # Generic Filters
    ######################################################

    def filter_min(self, column, value):

        if column not in self.df.columns:
            return

        self.df = self.df[
            self.df[column] >= value
        ]

    def filter_max(self, column, value):

        if column not in self.df.columns:
            return

        self.df = self.df[
            self.df[column] <= value
        ]

    ######################################################
    # Composite Score
    ######################################################

    def compute_composite_score(self):

        score = pd.Series(0,index=self.df.index,dtype=float)

        if "return_on_equity_pct" in self.df.columns:

            score += (
                self.df["return_on_equity_pct"]
                .fillna(0)
                .clip(0,30)
                /30
            )*25

        if "revenue_cagr_5yr" in self.df.columns:

            score += (
                self.df["revenue_cagr_5yr"]
                .fillna(0)
                .clip(0,30)
                /30
            )*20

        if "pat_cagr_5yr" in self.df.columns:

            score += (
                self.df["pat_cagr_5yr"]
                .fillna(0)
                .clip(0,30)
                /30
            )*20

        if "free_cash_flow_cr" in self.df.columns:

            score += (
                (
                    self.df["free_cash_flow_cr"]
                    >0
                ).astype(int)
            )*15

        if "debt_to_equity" in self.df.columns:

            debt_score = (
                1-
                self.df["debt_to_equity"]
                .fillna(5)
                .clip(0,5)/5
            )*20

            score += debt_score

        self.df["composite_quality_score"]=score.round(2)

    ######################################################
    # Individual Filters
    ######################################################

    def roe(self,value):
        self.filter_min(
            "return_on_equity_pct",
            value
        )

    def de(self,value):

        if "broad_sector" in self.df.columns:

            financials = self.df[
                self.df["broad_sector"]=="Financials"
            ]

            others = self.df[
                self.df["broad_sector"]!="Financials"
            ]

            others = others[
                others["debt_to_equity"]<=value
            ]

            self.df = pd.concat(
                [
                    financials,
                    others
                ]
            )

        else:

            self.filter_max(
                "debt_to_equity",
                value
            )

    def fcf(self,value):
        self.filter_min(
            "free_cash_flow_cr",
            value
        )

    def revenue_growth(self,value):
        self.filter_min(
            "revenue_cagr_5yr",
            value
        )

    def pat_growth(self,value):
        self.filter_min(
            "pat_cagr_5yr",
            value
        )

    def opm(self,value):
        self.filter_min(
            "operating_profit_margin_pct",
            value
        )

    #def pe(self,value):
    #    self.filter_max(
    #        "pe_ratio",
    #        value
    #    )

    #def pb(self,value):
    #    self.filter_max(
    #        "pb_ratio",
    #        value
    #    )

    #def dividend(self,value):
    #    self.filter_min(
    #        "dividend_yield_pct",
    #        value
    #    )

    def icr(self, value):

        if "interest_coverage" not in self.df.columns:
            return

        temp = self.df.copy()

        # Debt Free companies always pass
        temp.loc[
            temp["interest_coverage"].isna(),
            "interest_coverage"
        ] = np.inf

        self.df = temp[
            temp["interest_coverage"] >= value
        ]

    def market_cap(self, value):
        self.filter_min(
            "market_cap_crore",
            value
        )

    def net_profit(self, value):

        if "net_profit" in self.df.columns:

            self.filter_min(
                "net_profit",
                value
            )

    def eps_growth(self, value):

        self.filter_min(
            "eps_cagr_5yr",
            value
        )

    def asset_turnover(self, value):

        self.filter_min(
            "asset_turnover",
            value
        )

    def sales(self, value):

        if "sales" in self.df.columns:

            self.filter_min(
                "sales",
                value
            )

    ######################################################
    # PRESET SCREENERS
    ######################################################

    def quality_compounder(self):

        self.roe(15)
        self.de(1.0)
        self.fcf(0)
        self.revenue_growth(10)

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    def value_pick(self):

        #self.pe(20)
        #self.pb(3)
        self.de(2)
        #self.dividend(1)

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    def growth_accelerator(self):

        self.pat_growth(20)
        self.revenue_growth(15)
        self.de(2)

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    def dividend_champion(self):

        #self.dividend(2)

        if "dividend_payout_ratio_pct" in self.df.columns:

            self.df = self.df[
                self.df["dividend_payout_ratio_pct"] < 80
            ]

        self.fcf(0)

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    def debt_free_bluechip(self):

        self.df = self.df[
            self.df["debt_to_equity"] == 0
        ]

        self.roe(12)

        if "sales" in self.df.columns:

            self.sales(5000)

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    def turnaround_watch(self):

        self.filter_min(
            "revenue_cagr_3yr",
            10
        )

        if "free_cash_flow_cr" in self.df.columns:

            self.df = self.df[
                self.df["free_cash_flow_cr"] > 0
            ]

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )

    ######################################################
    # CUSTOM FILTER ENGINE
    ######################################################

    def apply_filters(self, config):

        if "roe_min" in config:
            self.roe(config["roe_min"])

        if "de_max" in config:
            self.de(config["de_max"])

        if "fcf_min" in config:
            self.fcf(config["fcf_min"])

        if "revenue_growth_min" in config:
            self.revenue_growth(
                config["revenue_growth_min"]
            )

        if "pat_growth_min" in config:
            self.pat_growth(
                config["pat_growth_min"]
            )

        if "opm_min" in config:
            self.opm(
                config["opm_min"]
            )

        #if "pe_max" in config:
        #    self.pe(
        #        config["pe_max"]
        #    )

        #if "pb_max" in config:
        #    self.pb(
        #        config["pb_max"]
        #    )

        #if "dividend_min" in config:
        #    self.dividend(
        #        config["dividend_min"]
        #    )

        if "icr_min" in config:
            self.icr(
                config["icr_min"]
            )

        if "market_cap_min" in config:
            self.market_cap(
                config["market_cap_min"]
            )

        self.compute_composite_score()

        return self.df.sort_values(
            "composite_quality_score",
            ascending=False
        )
    
    ######################################################
# Export Functions
######################################################

def export_screener():

    engine = ScreenerEngine()

    os.makedirs(
        "output",
        exist_ok=True
    )

    writer = pd.ExcelWriter(
        "output/screener_output.xlsx",
        engine="openpyxl"
    )

    presets = {

        "Quality Compounder": engine.quality_compounder,
        "Value Pick": engine.value_pick,
        "Growth Accelerator": engine.growth_accelerator,
        "Dividend Champion": engine.dividend_champion,
        "Debt Free Bluechip": engine.debt_free_bluechip,
        "Turnaround Watch": engine.turnaround_watch

    }

    summary = []

    for name, func in presets.items():

        print(f"Running {name}...")

        # Reload original dataframe
        engine.load_data()

        result = func()

        result.to_excel(
            writer,
            sheet_name=name[:31],
            index=False
        )

        summary.append({
            "Preset": name,
            "Companies Returned": len(result)
        })

        print(f"{len(result)} companies")

    pd.DataFrame(summary).to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

    writer.close()
    engine.conn.close()

    print()
    print("=" * 60)
    print("Screener Output Generated Successfully")
    print("=" * 60)
    print()
    print("Saved:")
    print("output/screener_output.xlsx")


######################################################
# Main
######################################################

if __name__ == "__main__":
    export_screener()

    