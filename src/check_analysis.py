import pandas as pd

df = pd.read_excel(
    "data/raw/analysis.xlsx",
    header=1
)

print(df.columns.tolist())
print()
print(df.head())