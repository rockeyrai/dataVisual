import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
file_2081 = BASE_DIR / "data" / "annual" / "annual8182.xlsx"

# -----------------------------
# READ FILE
# -----------------------------

df = pd.read_excel(file_2081, sheet_name="index")

# -----------------------------
# CLEAN DATA
# -----------------------------

# Clean column names
df.columns = df.columns.str.strip()

# Convert BUSINESS_DATE to datetime
df["BUSINESS_DATE"] = pd.to_datetime(df["BUSINESS_DATE"], errors="coerce")

# Sort properly and reset index
df = df.sort_values("BUSINESS_DATE").reset_index(drop=True)

# -----------------------------
# PLOT
# -----------------------------
selected_sectors = [
    "Hotels And Tourism Index",
    "Development Bank Index",
    "Manufacturing And Processing",
    "Life Insurance",
    "Non Life Insurance",
    "Microfinance Index"
]

selected_sectors2=[
        "Banking SubIndex",
    "Others Index",
    "Finance Index",
    "Trading Index"
]

selected_sectors3=[
    "Mutual Fund",
    "Investment Index"
]





# Plot all columns except BUSINESS_DATE
# for all sector 
# for col in df.columns:
#     if col != "BUSINESS_DATE":
#         plt.plot(df["BUSINESS_DATE"], df[col], label=col)


# for only selected sector 
# for col in selected_sectors:
#     if col in df.columns:
#         plt.plot(df["BUSINESS_DATE"], df[col], label=col)


# Normalize to Base 100
df_base = df.copy()

for col in selected_sectors:
    if col in df_base.columns:
        first_value = df_base[col].iloc[0]
        df_base[col] = (df_base[col] / first_value) * 100
        
plt.figure(figsize=(14, 7))

for col in selected_sectors:
    if col in df_base.columns:
        plt.plot(df_base["BUSINESS_DATE"], df_base[col], label=col)

# -----------------------------
# DETECT MONTH TRANSITIONS
# -----------------------------

# Detect month change using period comparison
month_change_mask = df["BUSINESS_DATE"].dt.to_period("M").ne(
    df["BUSINESS_DATE"].dt.to_period("M").shift()
)

# Remove first row
month_change_mask.iloc[0] = False

change_dates = df.loc[month_change_mask, "BUSINESS_DATE"]

# Draw vertical dashed lines at start of each new month
for date in change_dates:
    plt.axvline(
        x=date,
        linestyle="--",
        linewidth=1,
        alpha=0.7
    )

# -----------------------------
# FINAL TOUCH
# -----------------------------

plt.xlabel("Date")
plt.title("Index Data with Monthly Change Markers")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.axhline(y=100, linestyle="--", linewidth=1)
plt.ylabel("Index Value (Base 100)")

# Save image
output_file = BASE_DIR / "base_index_chart_8182.png"
plt.savefig(output_file, dpi=300)

print("Chart saved to:", output_file)

plt.show()
