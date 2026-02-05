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

output_path = BASE_DIR / "sector_2070_vs_2079_vs_2082.png"

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
    "MANUFACTURING AND PROCESSING":"Manufacturing",


    "Hotel": "Hotels",
    "Hotels And Tourism": "Hotels",
    "HOTELS AND TOURISM":"Hotels",

    "HydroPower": "Hydro Power",
    "Hydro Power": "Hydro Power",
    "HYDRO POWER":"Hydro Power",

    "Dev.Bank": "Development Bank",
    "Development Bank": "Development Bank",
    "DEVELOPMENT BANKS":"Development Bank",

    "Insurance": "Insurance",
    "LIFE INSURANCE":"Insurance",

    "MICROFINANCE":"Micro Finance",

    "INVESTMENT":"Investment",

    "Non Life Insurance": "Insurance",
    "NON LIFE INSURANCE":"Insurance",

    "Finance": "Finance",
    "FINANCE":"Finance",

    "Trading": "Trading",
    "TRADINGS":"Trading",

    "Others": "Others",
    "OTHERS":"Others"
}

df70 = df70.rename(columns=rename_map)
df79 = df79.rename(columns=rename_map)
df82 = df82.rename(columns=rename_map)

# -----------------------------
# Drop Date completely
# -----------------------------
df70 = df70.drop(columns=[c for c in df70.columns if c.lower() == "date"], errors="ignore")
df79 = df79.drop(columns=[c for c in df79.columns if c.lower() == "date"], errors="ignore")
df82 = df82.drop(columns=[c for c in df82.columns if c.lower() == "date"], errors="ignore")

# -----------------------------
# Keep only common sectors
# -----------------------------
common_sectors = sorted(set(df70.columns) & set(df79.columns))

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
# Normalize (Base = 100)
# -----------------------------
df70_norm = df70 / df70.iloc[0] * 100
df79_norm = df79 / df79.iloc[0] * 100
df82_norm = df82 / df82.iloc[0] * 100

# -----------------------------
# Plot sector-wise pattern comparison
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
    ax.plot(df70_norm.index, df70_norm[sector], label="2070", linewidth=2)
    ax.plot(df79_norm.index, df79_norm[sector], label="2079", linewidth=2)
    ax.plot(df82_norm.index, df82_norm[sector], label="2082", linewidth=2)

    ax.set_title(f"{sector} – Pattern Comparison (Date Ignored)", fontsize=14)
    ax.set_ylabel("Index (Base = 100)")
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel("Observation Index")

plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.close()

print("✅ Pattern-aligned sector comparison saved:")
print(output_path)
