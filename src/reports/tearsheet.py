import os
import sqlite3
import tempfile

import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Image,
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "db",
    "nifty100.db"
)


PROS_CONS_PATH = os.path.join(
    "output",
    "pros_cons_generated.csv",
)

CAPITAL_PATH = os.path.join(
    "output",
    "capital_allocation.csv",
)

OUTPUT_DIR = os.path.join(
    "reports",
    "tearsheets",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    "SELECT * FROM companies",
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

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn,
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

analysis = pd.read_sql(
    "SELECT * FROM analysis",
    conn,
)

pros_cons = pd.read_csv(PROS_CONS_PATH)

capital = pd.read_csv(CAPITAL_PATH)

# ---------------------------------------------------------
# Styles
# ---------------------------------------------------------

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontSize=24,
    alignment=TA_CENTER,
    textColor=colors.white,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    textColor=colors.darkblue,
    spaceAfter=10,
)

normal_style = styles["BodyText"]

bullet_green = ParagraphStyle(
    "Green",
    parent=normal_style,
    textColor=colors.darkgreen,
)

bullet_red = ParagraphStyle(
    "Red",
    parent=normal_style,
    textColor=colors.red,
)

kpi_style = ParagraphStyle(
    "KPI",
    parent=styles["Heading3"],
    alignment=TA_CENTER,
)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

# ---------------------------------------------------------
# Year Utilities
# ---------------------------------------------------------

import re


def extract_year(value):
    """
    Extracts a 4-digit year from different formats.

    Examples:
        Mar-24    -> 2024
        Sep2024   -> 2024
        Dec2016   -> 2016
        2025      -> 2025
    """

    value = str(value).strip()

    match = re.search(r"(20\d{2}|19\d{2})", value)
    if match:
        return int(match.group(1))

    match = re.search(r"-(\d{2})$", value)
    if match:
        yy = int(match.group(1))
        return 2000 + yy if yy <= 30 else 1900 + yy

    return None


def latest_year(df):
    """
    Returns the latest year's rows from a dataframe.
    """

    if df.empty:
        return df

    temp = df.copy()

    temp["year_num"] = (
        temp["year"]
        .apply(extract_year)
    )

    temp = temp.dropna(subset=["year_num"])

    temp["year_num"] = (
        temp["year_num"]
        .astype(int)
    )

    latest = temp["year_num"].max()

    return temp[
        temp["year_num"] == latest
    ]


# ---------------------------------------------------------
# Company Data
# ---------------------------------------------------------

def company_info(company_id):

    row = companies[
        companies["id"] == company_id
    ]

    if row.empty:
        return None

    return row.iloc[0]


def company_profit(company_id):

    df = profit[
        profit["company_id"] == company_id
    ].copy()

    return latest_year(df)


def company_balance(company_id):

    df = balance[
        balance["company_id"] == company_id
    ].copy()

    return latest_year(df)


def company_cashflow(company_id):

    df = cashflow[
        cashflow["company_id"] == company_id
    ].copy()

    return latest_year(df)


def company_ratios(company_id):

    df = ratios[
        ratios["company_id"] == company_id
    ].copy()

    return latest_year(df)


def company_analysis(company_id):

    df = analysis[
        analysis["company_id"] == company_id
    ]

    if df.empty:
        return None

    return df.iloc[0]


# ---------------------------------------------------------
# Pros & Cons
# ---------------------------------------------------------

def company_pros(company_id):

    return (
        pros_cons[
            (pros_cons["company_id"] == company_id)
            &
            (pros_cons["type"] == "PRO")
        ]
        .sort_values(
            "confidence_pct",
            ascending=False,
        )
    )


def company_cons(company_id):

    return (
        pros_cons[
            (pros_cons["company_id"] == company_id)
            &
            (pros_cons["type"] == "CON")
        ]
        .sort_values(
            "confidence_pct",
            ascending=False,
        )
    )


# ---------------------------------------------------------
# Capital Allocation
# ---------------------------------------------------------

def company_capital(company_id):

    df = capital[
        capital["company_id"] == company_id
    ]

    if df.empty:
        return "Not Available"

    latest = df.iloc[-1]

    if "capital_pattern" in latest.index:
        return latest["capital_pattern"]

    if "pattern" in latest.index:
        return latest["pattern"]

    return "Not Available"

# ---------------------------------------------------------
# Temporary chart folder
# ---------------------------------------------------------

TEMP_DIR = tempfile.mkdtemp()

# ---------------------------------------------------------
# Chart Helpers
# ---------------------------------------------------------

def save_chart(fig, filename):
    """
    Saves a matplotlib figure to the temporary directory.
    """
    path = os.path.join(TEMP_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def revenue_profit_chart(company_id):
    """
    Revenue vs Net Profit over the years
    """

    df = profit[
        profit["company_id"] == company_id
    ].copy()

    if df.empty:
        return None

    df = df.sort_values("year")

    fig, ax = plt.subplots(figsize=(5.5, 3.2))

    ax.plot(
        df["year"],
        df["sales"],
        marker="o",
        linewidth=2,
        label="Sales",
    )

    ax.plot(
        df["year"],
        df["net_profit"],
        marker="o",
        linewidth=2,
        label="Net Profit",
    )

    ax.set_title("Revenue vs Net Profit")
    ax.set_xlabel("Year")
    ax.legend()

    return save_chart(fig, f"{company_id}_revenue.png")


def roce_roe_chart(company_id):
    """
    ROCE & ROE comparison
    """

    company = company_info(company_id)

    if company is None:
        return None

    roce = company.get("roce_percentage", 0)
    roe = company.get("roe_percentage", 0)

    fig, ax = plt.subplots(figsize=(4.5,3))

    ax.bar(
        ["ROCE", "ROE"],
        [roce, roe]
    )

    ax.set_ylabel("%")
    ax.set_title("ROCE vs ROE")

    return save_chart(fig, f"{company_id}_roe.png")


def balance_chart(company_id):
    """
    Equity vs Borrowings vs Other Liabilities
    """

    df = company_balance(company_id)

    if df.empty:
        return None

    row = df.iloc[0]

    equity = (
        row["equity_capital"]
        +
        row["reserves"]
    )

    borrow = row["borrowings"]

    other = row["other_liabilities"]

    fig, ax = plt.subplots(figsize=(4.8,3))

    ax.bar(
        ["Capital"],
        [equity],
        label="Equity",
    )

    ax.bar(
        ["Capital"],
        [borrow],
        bottom=[equity],
        label="Borrowings",
    )

    ax.bar(
        ["Capital"],
        [other],
        bottom=[equity + borrow],
        label="Other",
    )

    ax.legend()

    ax.set_title("Balance Sheet Mix")

    return save_chart(fig, f"{company_id}_balance.png")


def cashflow_chart(company_id):
    """
    Operating / Investing / Financing cash flow
    """

    df = company_cashflow(company_id)

    if df.empty:
        return None

    row = df.iloc[0]

    labels = [
        "Operating",
        "Investing",
        "Financing",
    ]

    values = [
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
    ]

    fig, ax = plt.subplots(figsize=(5,3))

    ax.bar(
        labels,
        values,
    )

    ax.axhline(
        0,
        linewidth=1,
    )

    ax.set_title("Cash Flow")

    return save_chart(fig, f"{company_id}_cashflow.png")


def operating_margin_chart(company_id):
    """
    Operating Margin through time
    """

    df = profit[
        profit["company_id"] == company_id
    ].copy()

    if df.empty:
        return None

    df = df.sort_values("year")

    fig, ax = plt.subplots(figsize=(5,3))

    ax.plot(
        df["year"],
        df["opm_percentage"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Operating Margin %")

    return save_chart(fig, f"{company_id}_opm.png")