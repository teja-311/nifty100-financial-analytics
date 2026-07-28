import pandas as pd
import os
import re

def extract_year(value):
    value = str(value).strip()

    # Match 4-digit year (e.g. Mar 2024, Dec2016)
    m = re.search(r"(20\d{2}|19\d{2})", value)
    if m:
        return int(m.group(1))

    # Match 2-digit year after dash (e.g. Mar-24)
    m = re.search(r"-(\d{2})$", value)
    if m:
        yy = int(m.group(1))
        return 2000 + yy if yy <= 30 else 1900 + yy

    return None


OUTPUT_DIR = "output"

capital = pd.read_csv(os.path.join(OUTPUT_DIR, "capital_allocation.csv"))

print(sorted(capital["year"].astype(str).unique()))

cashflow = pd.read_excel(
    os.path.join(OUTPUT_DIR, "cashflow_intelligence.xlsx")
)

# --------------------------------------------------
# Verify completeness
# --------------------------------------------------

print("=" * 60)
print("Capital Allocation Verification")
print("=" * 60)

print("Rows :", len(capital))
print("Companies :", capital["company_id"].nunique())
print("Years :", capital["year"].nunique())

# --------------------------------------------------
# Latest year
# --------------------------------------------------

capital["year_num"] = capital["year"].apply(extract_year)

capital = capital.dropna(subset=["year_num"])

capital["year_num"] = capital["year_num"].astype(int)

latest_year = capital["year_num"].max()

latest = capital[
    capital["year_num"] == latest_year
].copy()

print(latest[["company_id", "year"]].head(20))
print("Latest rows:", len(latest))

# --------------------------------------------------
# Distribution summary
# --------------------------------------------------

distribution = (
    latest["capital_pattern"]
    .value_counts()
    .rename_axis("capital_pattern")
    .reset_index(name="company_count")
)

distribution.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "capital_pattern_distribution.csv",
    ),
    index=False,
)

print("\nLatest Year :", latest_year)
print(distribution)

# --------------------------------------------------
# Add capital allocation column
# --------------------------------------------------

cashflow = cashflow.merge(
    latest[
        [
            "company_id",
            "capital_pattern",
        ]
    ],
    on="company_id",
    how="left",
)

cashflow.to_excel(
    os.path.join(
        OUTPUT_DIR,
        "cashflow_intelligence.xlsx",
    ),
    index=False,
)

# --------------------------------------------------
# Pattern changes
# --------------------------------------------------

capital = capital.sort_values(
    [
        "company_id",
        "year",
    ]
)

changes = []

for company, grp in capital.groupby("company_id"):

    grp = grp.reset_index(drop=True)

    for i in range(1, len(grp)):

        previous = grp.loc[i - 1, "capital_pattern"]
        current = grp.loc[i, "capital_pattern"]

        if previous != current:

            changes.append(
                {
                    "company_id": company,
                    "year": grp.loc[i, "year"],
                    "previous_pattern": previous,
                    "current_pattern": current,
                }
            )

changes = pd.DataFrame(changes)

changes.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "pattern_changes.csv",
    ),
    index=False,
)

print("\nPattern Changes :", len(changes))

print("\nGenerated:")
print("- capital_pattern_distribution.csv")
print("- pattern_changes.csv")
print("- Updated cashflow_intelligence.xlsx")