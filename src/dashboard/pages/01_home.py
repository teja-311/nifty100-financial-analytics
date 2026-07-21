import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors
)

st.title("🏠 Home Dashboard")

companies = get_companies()
ratios = get_ratios()
sectors = get_sectors()

# ---------------- KPI Cards ----------------

c1, c2, c3 = st.columns(3)

with c1:
    if "return_on_equity_pct" in ratios.columns:
        st.metric(
            "Average ROE",
            round(
                ratios["return_on_equity_pct"].mean(),
                2
            )
        )

with c2:
    if "debt_to_equity" in ratios.columns:
        st.metric(
            "Average D/E",
            round(
                ratios["debt_to_equity"].mean(),
                2
            )
        )

with c3:
    st.metric(
        "Companies",
        len(companies)
    )

st.divider()

# ---------------- Sector Distribution ----------------

st.subheader("Sector Distribution")

if len(sectors):

    fig = px.pie(
        sectors,
        names="broad_sector",
        title="Companies by Sector"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ---------------- Top Companies ----------------

st.subheader("Top Companies by ROE")

if "return_on_equity_pct" in ratios.columns:

    top = (
        ratios
        .sort_values(
            "return_on_equity_pct",
            ascending=False
        )
        [["company_id","return_on_equity_pct"]]
        .head(10)
    )

    st.dataframe(
        top,
        use_container_width=True
    )