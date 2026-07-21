import streamlit as st
import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from utils.db import get_documents

st.title("📄 Annual Reports")

df = get_documents()

if df.empty:

    st.warning("No annual reports available.")

else:

    company = st.selectbox(
        "Select Company",
        sorted(df["company_name"].dropna().unique())
    )

    reports = (

        df[df["company_name"] == company]

        .sort_values("year", ascending=False)

    )

    st.dataframe(
        reports[["year", "annual_report"]],
        use_container_width=True
    )

    st.subheader("Download Reports")

    for _, row in reports.iterrows():

        st.markdown(
            f"**{row['year']}** — [Annual Report]({row['annual_report']})"
        )