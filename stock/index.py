import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------- Paths ----------
script_dir = os.path.dirname(os.path.abspath(__file__))

marketcap_path = os.path.join(script_dir, "data.json")
summary_path = os.path.join(script_dir, "marketsummary.json")

# ---------- Load JSON ----------
with open(marketcap_path, "r") as file:
    marketcap_data = json.load(file)

with open(summary_path, "r") as file:
    summary_data = json.load(file)

# ---------- Convert to DataFrames ----------
df_cap = pd.DataFrame(marketcap_data)
df_sum = pd.DataFrame(summary_data)

# ---------- Convert date columns ----------
df_cap["businessDate"] = pd.to_datetime(df_cap["businessDate"])
df_sum["businessDate"] = pd.to_datetime(df_sum["businessDate"])

# ---------- Set index ----------
df_cap.set_index("businessDate", inplace=True)
df_sum.set_index("businessDate", inplace=True)

# ---------- Sort by date ----------
df_cap.sort_index(inplace=True)
df_sum.sort_index(inplace=True)

# ---------- NEW: Average Turnover per Traded Scrip ----------
df_sum["avgTurnoverPerScrip"] = (
    df_sum["totalTurnover"] / df_sum["tradedScrips"]
)

df_sum["totalTurnover_scaled"] = df_sum["totalTurnover"] / 1e2


def get_unique_filename(base_name, extension=".png"):
    counter = 0
    filename = f"{base_name}{extension}"

    while os.path.exists(filename):
        counter += 1
        filename = f"{base_name}_{counter}{extension}"

    return filename


# ---------- Plot ----------
plt.figure(figsize=(12, 9))

# ---- Subplot 1: Market Capitalization ----
plt.subplot(2, 1, 1)
plt.plot(df_cap.index, df_cap["marCap"], label="Market Cap")
plt.plot(df_cap.index, df_cap["floatMarCap"], label="Float Market Cap")
plt.plot(df_cap.index, df_cap["senMarCap"], label="Sensitive Market Cap")
plt.plot(df_cap.index, df_cap["senFloatMarCap"], label="Sensitive Float Market Cap")

plt.title("Market Capitalization Over Time")
plt.ylabel("Market Cap Value")
plt.legend()
plt.grid(True)

# ---- Subplot 2: Market Activity + Quality ----
plt.subplot(2, 1, 2)
plt.plot(df_sum.index, df_sum["totalTurnover_scaled"], label="Total Turnover (×1e2)")
plt.plot(df_sum.index, df_sum["totalTradedShares"], label="total TradedShares")
plt.plot(df_sum.index, df_sum["totalTransactions"], label="total Transactions")
plt.plot(df_sum.index, df_sum["avgTurnoverPerScrip"], label="Avg Turnover per Scrip")

plt.title("Market Activity & Breadth Quality")
plt.xlabel("Business Date")
plt.ylabel("Value")
plt.legend()
plt.grid(True)

# ---------- Finalize ----------
plt.tight_layout()

output_file = get_unique_filename("market_overview")
plt.savefig(output_file, dpi=300)

print(f"Chart saved as {output_file}")

