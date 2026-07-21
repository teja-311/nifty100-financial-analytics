import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import get_peers, get_ratios

st.title("🤝 Peer Comparison")

peers = get_peers()
ratios = get_ratios()

peer_groups = sorted(
    peers["peer_group_name"].unique()
)

selected_group = st.selectbox(
    "Peer Group",
    peer_groups
)

companies = peers[
    peers["peer_group_name"] == selected_group
]

df = ratios.merge(
    companies,
    on="company_id",
    how="inner"
)

st.success(
    f"{len(companies)} companies in this peer group"
)

if len(df):

    chart = px.bar(
        df,
        x="company_id",
        y="return_on_equity_pct",
        color="company_id",
        title="ROE Comparison"
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )

    st.dataframe(
        df,
        use_container_width=True
    )