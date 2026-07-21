from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("💰 Capital Allocation")

BASE_DIR = Path(__file__).resolve().parents[3]

csv_path = BASE_DIR / "output" / "capital_allocation.csv"

try:

    df = pd.read_csv(csv_path)

    latest = (
        df.sort_values("year")
            .groupby("company_id")
            .last()
            .reset_index()
    )

    fig = px.treemap(
        latest,
        path=["capital_pattern", "company_id"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        latest,
        use_container_width=True
    )

except Exception as e:

    st.error(f"Error: {e}")