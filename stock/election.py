import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

file_2070 = BASE_DIR / "data" / "monthly" / "data2070.xlsx"
file_2079 = BASE_DIR / "data" / "monthly" / "data2079.xlsx"
file_2082 = BASE_DIR / "data" / "monthly" / "data2082.xlsx"

output_path = BASE_DIR / "sector_momentum_2070_vs_2079_vs_2082.png"

# -----------------------------
# Read Excel files
# -----------------------------
df70 = pd.read_excel(file_2070)
df79 = pd.read_excel(file_2079)
df82 = pd.read_excel(file_2082)

# -----------------------------
# Clean column headers
# -----------------------------
def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("-", "", regex=False)
        .str.replace("  ", " ")
    )
    return df

df70 = clean_columns(df70)
df79 = clean_columns(df79)
df82 = clean_columns(df82)

# -----------------------------
# Normalize sector names
# -----------------------------
rename_map = {
    "Com Bank": "Commercial Bank",
    "Com. Bank": "Commercial Bank",
    "COMMERCIAL BANKS": "Commercial Bank",

    "Manufacturing and Processing": "Manufacturing",
    "Manufact": "Manufacturing",
    "MANUFACTURING AND PROCESSING": "Manufacturing",

    "Hotel": "Hotels",
    "Hotels And Tourism": "Hotels",
    "HOTELS AND TOURISM": "Hotels",

    "HydroPower": "Hydro Power",
    "HYDRO POWER": "Hydro Power",

    "Dev.Bank": "Development Bank",
    "DEVELOPMENT BANKS": "Development Bank",

    "Insurance": "Insurance",
    "LIFE INSURANCE": "Insurance",
    "NON LIFE INSURANCE": "Insurance",

    "MICROFINANCE": "Micro Finance",

    "INVESTMENT": "Investment",

    "FINANCE": "Finance",

    "Trading": "Trading",
    "TRADINGS": "Trading",

    "Others": "Others",
    "OTHERS": "Others"
}

df70 = df70.rename(columns=rename_map)
df79 = df79.rename(columns=rename_map)
df82 = df82.rename(columns=rename_map)

# -----------------------------
# Drop Date completely
# -----------------------------
def drop_date(df):
    return df.drop(columns=[c for c in df.columns if c.lower() == "date"], errors="ignore")

df70 = drop_date(df70)
df79 = drop_date(df79)
df82 = drop_date(df82)

# -----------------------------
# Keep only common sectors
# -----------------------------
common_sectors = sorted(set(df70.columns) & set(df79.columns) & set(df82.columns))

df70 = df70[common_sectors]
df79 = df79[common_sectors]
df82 = df82[common_sectors]

# -----------------------------
# Reset index → same timeline
# -----------------------------
df70 = df70.reset_index(drop=True)
df79 = df79.reset_index(drop=True)
df82 = df82.reset_index(drop=True)

# -----------------------------
# Calculate % change (Momentum)
# -----------------------------
df70_pct = df70.pct_change() * 100
df79_pct = df79.pct_change() * 100
df82_pct = df82.pct_change() * 100

# -----------------------------
# Plot sector-wise momentum comparison
# -----------------------------
fig, axes = plt.subplots(
    nrows=len(common_sectors),
    ncols=1,
    figsize=(18, 4 * len(common_sectors)),
    sharex=True
)

if len(common_sectors) == 1:
    axes = [axes]

for ax, sector in zip(axes, common_sectors):
    ax.plot(df70_pct.index, df70_pct[sector], label="2070", linewidth=1.8)
    ax.plot(df79_pct.index, df79_pct[sector], label="2079", linewidth=1.8)
    ax.plot(df82_pct.index, df82_pct[sector], label="2082", linewidth=1.8)

    ax.axhline(0, linewidth=1)  # zero line = expansion vs contraction
    ax.set_title(f"{sector} – % Change (Momentum View, Date Ignored)", fontsize=14)
    ax.set_ylabel("% Change")
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel("Observation Index")

plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.close()

print("✅ Sector momentum comparison saved:")
print(output_path)
