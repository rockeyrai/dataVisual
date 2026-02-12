import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
file_2081 = BASE_DIR / "data" / "annual" / "main.xlsx"

# -----------------------------
# READ FILE
# -----------------------------

df = pd.read_excel(file_2081, sheet_name="Sheet1")

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



# =============================
# ROTATION BACKTEST FUNCTION
# =============================

def rotation_backtest(df_base, lookback=20, transaction_cost=0.002):

    momentum = df_base.pct_change(lookback)

    # Remove rows where momentum is all NaN
    momentum = momentum.dropna(how="all")

    daily_returns = df_base.pct_change().fillna(0)

    leader = momentum.idxmax(axis=1)

    strategy_returns = []
    current_sector = None

    for date in df_base.index:

        if date not in leader.index:
            strategy_returns.append(0)
            continue

        new_sector = leader.loc[date]

        if current_sector is not None and new_sector != current_sector:
            cost = transaction_cost
        else:
            cost = 0

        daily_ret = daily_returns.loc[date, new_sector] - cost
        strategy_returns.append(daily_ret)

        current_sector = new_sector

    strategy_returns = pd.Series(strategy_returns, index=df_base.index)

    equity_curve = (1 + strategy_returns).cumprod()

    total_return = equity_curve.iloc[-1] - 1

    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_dd = drawdown.min()

    sharpe = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(252)

    return {
        "Lookback": lookback,
        "Total Return %": total_return * 100,
        "Max Drawdown %": max_dd * 100,
        "Sharpe Ratio": sharpe,
        "Equity Curve": equity_curve
    }


rotation_table = pd.DataFrame({
    "From": leader.shift(),
    "To": leader
})

rotation_table = rotation_table[rotation_table["From"] != rotation_table["To"]]
rotation_table = rotation_table.dropna()

print("\n================ ROTATION TABLE ================\n")
print(rotation_table)


transition_matrix = pd.crosstab(rotation_table["From"], rotation_table["To"])
print("\n================ TRANSITION MATRIX ================\n")
print(transition_matrix.to_string())

# =============================
# OPTIMAL LOOKBACK TEST
# =============================

lookbacks = [10, 20, 30, 60, 90, 120]

results = []

for lb in lookbacks:
    result = rotation_backtest(df_base, lookback=lb, transaction_cost=0.002)
    results.append(result)

results_df = pd.DataFrame(results).drop(columns=["Equity Curve"])

print("\n================ ROTATION STRATEGY RESULTS ================\n")
print(results_df.sort_values("Sharpe Ratio", ascending=False).round(2))




best_lb = results_df.sort_values("Sharpe Ratio", ascending=False).iloc[0]["Lookback"]

best_result = rotation_backtest(df_base, lookback=int(best_lb), transaction_cost=0.002)

plt.figure(figsize=(12,6))
plt.plot(best_result["Equity Curve"])
plt.title(f"Best Rotation Strategy (Lookback={int(best_lb)})")
plt.xlabel("Date")
plt.ylabel("Growth of $1")
plt.show()

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

output_file = BASE_DIR / "base_main_0.png"
plt.savefig(output_file, dpi=300)

print("\nChart saved to:", output_file)

plt.show()
