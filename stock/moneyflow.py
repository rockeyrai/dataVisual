import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
file_2081 = BASE_DIR / "data" / "annual" / "annual8182.xlsx"

# -----------------------------
# READ FILE
# -----------------------------

df = pd.read_excel(file_2081, sheet_name="index")

# -----------------------------
# CLEAN DATA
# -----------------------------

df.columns = df.columns.str.strip()
df["BUSINESS_DATE"] = pd.to_datetime(df["BUSINESS_DATE"], errors="coerce")
df = df.sort_values("BUSINESS_DATE").reset_index(drop=True)

# -----------------------------
# SELECT SECTORS
# -----------------------------

# selected_sectors = [
#     "Hotels And Tourism Index",
#     "Development Bank Index",
#     "Manufacturing And Processing",
#     "Life Insurance",
#     "Non Life Insurance",
#     "Microfinance Index"
# ]
selected_sectors = df.columns.drop("BUSINESS_DATE")

# Keep only existing columns
selected_sectors = [col for col in selected_sectors if col in df.columns]

sector_df = df[selected_sectors].copy()

# -----------------------------
# BASE 100 NORMALIZATION
# -----------------------------

df_base = sector_df / sector_df.iloc[0] * 100

# -----------------------------
# 📊 CORRELATION MATRIX
# -----------------------------

returns = sector_df.pct_change().dropna()
correlation_matrix = returns.corr()

print("\n================ CORRELATION MATRIX ================\n")
print(correlation_matrix.round(2))

# -----------------------------
# 📈 SECTOR LEADERSHIP RANKING
# -----------------------------

total_return = (df_base.iloc[-1] - 100)
ranking = total_return.sort_values(ascending=False)

print("\n================ SECTOR LEADERSHIP RANKING (%) ================\n")
print(ranking.round(2))


# -----------------------------
# 🔁 AUTOMATIC ROTATION DETECTION (FIXED)
# -----------------------------

rolling_perf = df_base.pct_change(20)

# Drop rows where all values are NaN
rolling_perf = rolling_perf.dropna(how="all")

# Detect leader
leader = rolling_perf.idxmax(axis=1)

# Detect leader change
rotation_points = leader.ne(leader.shift())

rotation_dates = df.loc[leader.index[rotation_points], "BUSINESS_DATE"]

print("\n================ ROTATION DATES ================\n")
print(rotation_dates)


# -----------------------------
# 📉 MAX DRAWDOWN
# -----------------------------

def max_drawdown(series):
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    return drawdown.min() * 100

drawdowns = df_base.apply(max_drawdown)

print("\n================ MAX DRAWDOWN (%) ================\n")
print(drawdowns.round(2))

# -----------------------------
# 📋 SUMMARY TABLE
# -----------------------------

summary = pd.DataFrame({
    "Total Return %": total_return,
    "Max Drawdown %": drawdowns
}).sort_values("Total Return %", ascending=False)

print("\n================ SUMMARY TABLE ================\n")
print(summary.round(2))

# -----------------------------
# 📊 PLOT BASE 100
# -----------------------------

plt.figure(figsize=(14, 7))

for col in selected_sectors:
    plt.plot(df["BUSINESS_DATE"], df_base[col], label=col)

# -----------------------------
# DETECT MONTH TRANSITIONS
# -----------------------------

month_change_mask = df["BUSINESS_DATE"].dt.to_period("M").ne(
    df["BUSINESS_DATE"].dt.to_period("M").shift()
)
month_change_mask.iloc[0] = False
change_dates = df.loc[month_change_mask, "BUSINESS_DATE"]

for date in change_dates:
    plt.axvline(x=date, linestyle="--", linewidth=1, alpha=0.5)

# -----------------------------
# FINAL TOUCH
# -----------------------------

plt.axhline(y=100, linestyle="--", linewidth=1)
plt.xlabel("Date")
plt.ylabel("Index Value (Base 100)")
plt.title("Base 100 Sector Comparison with Monthly Markers")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

output_file = BASE_DIR / "base_index_chart_8182.png"
plt.savefig(output_file, dpi=300)

print("\nChart saved to:", output_file)

plt.show()
