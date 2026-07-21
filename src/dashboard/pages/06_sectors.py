import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import get_sectors

st.title("🏭 Sector Analysis")

df = get_sectors()

sector = st.selectbox(
    "Sector",
    sorted(df["broad_sector"].unique())
)

filtered = df[
    df["broad_sector"] == sector
]

fig = px.histogram(
    filtered,
    x="sub_sector",
    color="sub_sector"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(filtered)