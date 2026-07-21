import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import get_pl

st.title("📈 Trend Analysis")

df = get_pl()

company = st.selectbox(
    "Company",
    sorted(df["company_id"].unique())
)

metric = st.selectbox(
    "Metric",
    [
        "sales",
        "net_profit",
        "operating_profit",
        "expenses"
    ]
)

data = df[df["company_id"] == company].copy()

# Remove TTM rows
data = data[data["year"].astype(str) != "TTM"]

# Extract a valid 4-digit year
data["year_num"] = (
    data["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

# Remove rows where no valid year was found
data = data.dropna(subset=["year_num"])

# Convert to integer
data["year_num"] = data["year_num"].astype(int)

# Sort chronologically
data = data.sort_values("year_num")

fig = px.line(
    data,
    x="year_num",
    y=metric,
    markers=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)