import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import (
    get_companies,
    get_ratios,
    get_pl
)

st.title("🏢 Company Profile")

companies = get_companies()
ratios = get_ratios()
pl = get_pl()

company_list = sorted(companies["id"].dropna().unique())

ticker = st.selectbox(
    "Select Company",
    company_list
)

company = companies[
    companies["id"] == ticker
]

ratio = ratios[
    ratios["company_id"] == ticker
]

history = pl[
    pl["company_id"] == ticker
]

if company.empty:

    st.error("Ticker not found.")

    st.stop()

st.subheader(company.iloc[0]["company_name"])

c1, c2, c3 = st.columns(3)

latest = ratio.tail(1)

if not latest.empty:

    with c1:

        st.metric(
            "ROE",
            latest.iloc[0]["return_on_equity_pct"]
        )

    with c2:

        st.metric(
            "Debt / Equity",
            latest.iloc[0]["debt_to_equity"]
        )

    with c3:

        st.metric(
            "Revenue CAGR",
            latest.iloc[0]["revenue_cagr_5yr"]
        )

st.divider()

if len(history):

    history = history.copy()

    history["year_num"] = (
        history["year"]
        .str[-4:]
        .replace("TTM", None)
    )

    history = history[
        history["year_num"].notna()
    ]

    history["year_num"] = history[
        "year_num"
    ].astype(int)

    history = history.sort_values(
        "year_num"
    )

    fig = px.bar(

        history,

        x="year_num",

        y="sales",

        title="Revenue"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.line(

        history,

        x="year_num",

        y="net_profit",

        title="Net Profit"

    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )