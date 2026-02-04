import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Path setup
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "data" / "monthly" / "2070Mangsir.xlsx"

# -----------------------------
# Read raw Excel
# -----------------------------
df_raw = pd.read_excel(
    file_path,
    sheet_name="Market Capitalization",
    header=None
)

# -----------------------------
# Combine multi-row headers
# -----------------------------
header_row_1 = df_raw.iloc[3].fillna("")
header_row_2 = df_raw.iloc[4].fillna("")

combined_headers = [
    f"{a} {b}".strip().replace("  ", " ")
    for a, b in zip(header_row_1, header_row_2)
]

# -----------------------------
# Create cleaned dataframe
# -----------------------------
df = df_raw.iloc[5:].copy()
df.columns = combined_headers
df.reset_index(drop=True, inplace=True)

# -----------------------------
# Rename columns (clean names)
# -----------------------------
df = df.rename(columns={
    "Date": "Date",
    "Com. Bank": "Commercial Bank",
    "Manufact- & Pros.": "Manufacturing",
    "Hotel": "Hotel",
    "Others": "Others",
    "Hydro Power": "Hydropower",
    "Trading": "Trading",
    "Insurance": "Insurance",
    "Finance": "Finance",
    "Dev. Bank": "Development Bank"
})

# -----------------------------
# Select sector-wise data
# -----------------------------
sector_columns = [
    "Commercial Bank",
    "Manufacturing",
    "Hotel",
    "Others",
    "Hydropower",
    "Trading",
    "Insurance",
    "Finance",
    "Development Bank"
]

sector_df = df[["Date"] + sector_columns]

# -----------------------------
# Clean data types
# -----------------------------
sector_df["Date"] = pd.to_datetime(sector_df["Date"])

for col in sector_columns:
    sector_df[col] = pd.to_numeric(sector_df[col], errors="coerce")

# -----------------------------
# Visualization
# -----------------------------
fig = px.line(
    sector_df,
    x="Date",
    y=sector_columns,
    title="NEPSE Sector-wise Market Capitalization",
    labels={
        "value": "Market Cap (Rs. in millions)",
        "variable": "Sector"
    }
)

fig.show()
