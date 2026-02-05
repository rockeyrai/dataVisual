import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

# file_2071 = BASE_DIR / "data" / "nonelection" / "data2071.xlsx"
file_2081 = BASE_DIR / "data" / "nonelection" / "data2081.xlsx"
file_2080 = BASE_DIR / "data" / "nonelection" / "data2080.xlsx"

output_path = BASE_DIR / "sector_momentum_2071_vs_2080_vs_2081.png"

# -----------------------------
# Read Excel files
# -----------------------------
# df71 = pd.read_excel(file_2071)
df81 = pd.read_excel(file_2081)
df80 = pd.read_excel(file_2080)

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

# df71 = clean_columns(df71)
df81 = clean_columns(df81)
df80 = clean_columns(df80)

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
    "LIFE INSURANCE": "Life Insurance",
    "NON LIFE INSURANCE": "Non Life Insurance",

    "MICROFINANCE": "Micro Finance",

    "INVESTMENT": "Investment",

    "FINANCE": "Finance",

    "Trading": "Trading",
    "TRADINGS": "Trading",

    "Others": "Others",
    "OTHERS": "Others"
}

# df71 = df71.rename(columns=rename_map)
df81 = df81.rename(columns=rename_map)
df80 = df80.rename(columns=rename_map)

# -----------------------------
# Drop Date completely
# -----------------------------
def drop_date(df):
    return df.drop(columns=[c for c in df.columns if c.lower() == "date"], errors="ignore")

# df71 = drop_date(df71)
df81 = drop_date(df81)
df80 = drop_date(df80)

# -----------------------------
# Keep only common sectors
# -----------------------------
common_sectors = sorted(set(df81.columns) & set(df80.columns))

# df71 = df71[common_sectors]
df81 = df81[common_sectors]
df80 = df80[common_sectors]

# -----------------------------
# Reset index → same timeline
# -----------------------------
# df71 = df71.reset_index(drop=True)
df81 = df81.reset_index(drop=True)
df80 = df80.reset_index(drop=True)

# -----------------------------
# Calculate % change (Momentum)
# -----------------------------
# df71_pct = df71.pct_change().iloc[1:] * 100
df80_pct = df80.pct_change().iloc[1:] * 100
df81_pct = df81.pct_change().iloc[1:] * 100

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
    # ax.plot(df71_pct.index, df71_pct[sector], label="2071", linewidth=1.8)
    ax.plot(df81_pct.index, df81_pct[sector], label="2081", linewidth=1.8)
    ax.plot(df80_pct.index, df80_pct[sector], label="2080", linewidth=1.8)

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
