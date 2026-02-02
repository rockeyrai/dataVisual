import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------- Paths ----------
script_dir = os.path.dirname(os.path.abspath(__file__))

marketcap_path = os.path.join(script_dir, "data.json")
summary_path = os.path.join(script_dir, "marketsummary.json")
sector_path = os.path.join(script_dir, "nepse_sector_data.csv")

# ---------- Load JSON ----------
with open(marketcap_path, "r") as file:
    marketcap_data = json.load(file)

with open(summary_path, "r") as file:
    summary_data = json.load(file)

# ---------- Load CSV ----------
df_sector = pd.read_csv(sector_path)

# ---------- Convert to DataFrames ----------
df_cap = pd.DataFrame(marketcap_data)
df_sum = pd.DataFrame(summary_data)

# ---------- Convert date columns ----------
df_cap["businessDate"] = pd.to_datetime(df_cap["businessDate"])
df_sum["businessDate"] = pd.to_datetime(df_sum["businessDate"])
df_sector["businessDate"] = pd.to_datetime(df_sector["businessDate"], errors="coerce")

# ---------- Remove invalid sector rows ----------
df_sector = df_sector[df_sector["businessDate"].dt.year >= 2000]

# ---------- Set index ----------
df_cap.set_index("businessDate", inplace=True)
df_sum.set_index("businessDate", inplace=True)
df_sector.set_index("businessDate", inplace=True)

# ---------- Sort ----------
df_cap.sort_index(inplace=True)
df_sum.sort_index(inplace=True)
df_sector.sort_index(inplace=True)

# ---------- Metrics ----------
df_sum["avgTurnoverPerScrip"] = (
    df_sum["totalTurnover"] / df_sum["tradedScrips"]
)

df_sum["totalTurnover_scaled"] = df_sum["totalTurnover"] / 1e2

# ---------- File name helper ----------
def get_unique_filename(base_name, extension=".png"):
    counter = 0
    filename = f"{base_name}{extension}"
    while os.path.exists(filename):
        counter += 1
        filename = f"{base_name}_{counter}{extension}"
    return filename

# ---------- Select Top 5 Sectors by Total Turnover ----------
top_sectors = (
    df_sector.groupby("sectorName")["turnOverValues"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

df_sector_top = df_sector[df_sector["sectorName"].isin(top_sectors)]

# ---------- Plot ----------
plt.figure(figsize=(14, 14))

# ---- Subplot 1: Market Capitalization ----
plt.subplot(3, 1, 1)
plt.plot(df_cap.index, df_cap["marCap"], label="Market Cap")
plt.plot(df_cap.index, df_cap["floatMarCap"], label="Float Market Cap")
plt.plot(df_cap.index, df_cap["senMarCap"], label="Sensitive Market Cap")
plt.plot(df_cap.index, df_cap["senFloatMarCap"], label="Sensitive Float Market Cap")

plt.title("Market Capitalization Over Time")
plt.ylabel("Market Cap Value")
plt.legend()
plt.grid(True)

# ---- Subplot 2: Market Activity & Quality ----
plt.subplot(3, 1, 2)
plt.plot(df_sum.index, df_sum["totalTurnover_scaled"], label="Total Turnover (×1e2)")
plt.plot(df_sum.index, df_sum["totalTradedShares"], label="Total Traded Shares")
plt.plot(df_sum.index, df_sum["totalTransactions"], label="Total Transactions")
plt.plot(df_sum.index, df_sum["avgTurnoverPerScrip"], label="Avg Turnover per Scrip")

plt.title("Market Activity & Breadth Quality")
plt.ylabel("Value")
plt.legend()
plt.grid(True)

# ---- Subplot 3: Sector-wise Turnover (Top 5) ----
plt.subplot(3, 1, 3)

for sector in top_sectors:
    sector_df = df_sector_top[df_sector_top["sectorName"] == sector]
    plt.plot(
        sector_df.index,
        sector_df["turnOverValues"],
        label=sector
    )

plt.title("Top 5 Sectors by Turnover")
plt.xlabel("Business Date")
plt.ylabel("Turnover Value")
plt.legend()
plt.grid(True)

# ---------- Finalize ----------
plt.tight_layout()

output_file = get_unique_filename("market_overview")
plt.savefig(output_file, dpi=300)
print(f"Chart saved as {output_file}")
