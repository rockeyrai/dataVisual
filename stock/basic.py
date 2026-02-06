import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

file_2080 = BASE_DIR / "data" / "nonelection" / "data2080.xlsx"
output_path = BASE_DIR / "basic_2080.png"

# -----------------------------
# Read Excel
# -----------------------------
df = pd.read_excel(file_2080)

# Convert DATE to datetime
df["DATE"] = pd.to_datetime(df["DATE"])

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(14, 8))

for column in df.columns:
    if column != "DATE":
        plt.plot(df["DATE"], df[column], label=column)

# -----------------------------
# Formatting
# -----------------------------
plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Sector-wise Market Data (2080)")
plt.legend(loc="upper left", fontsize=8)

plt.xticks(rotation=45)
plt.grid(True)

# -----------------------------
# Save & close
# -----------------------------
plt.tight_layout()
plt.savefig(output_path, dpi=300)
plt.close()
