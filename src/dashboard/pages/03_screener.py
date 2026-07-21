import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import get_ratios

st.title("🔎 Financial Screener")

df = get_ratios()

st.sidebar.header("Filters")

roe = st.sidebar.slider(
    "Minimum ROE",
    -100.0,
    100.0,
    15.0
)

de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    10.0,
    2.0
)

cagr = st.sidebar.slider(
    "Minimum Revenue CAGR",
    -50.0,
    100.0,
    10.0
)

filtered = df.copy()

if "return_on_equity_pct" in filtered.columns:
    filtered = filtered[
        filtered["return_on_equity_pct"] >= roe
    ]

if "debt_to_equity" in filtered.columns:
    filtered = filtered[
        filtered["debt_to_equity"] <= de
    ]

if "revenue_cagr_5yr" in filtered.columns:
    filtered = filtered[
        filtered["revenue_cagr_5yr"] >= cagr
    ]

st.success(f"{len(filtered)} companies found")

st.dataframe(
    filtered,
    use_container_width=True
)

csv = filtered.to_csv(index=False)

st.download_button(

    "Download CSV",

    csv,

    "screener.csv",

    "text/csv"

)