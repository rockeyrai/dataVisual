import json
import pandas as pd
import matplotlib.pyplot as plt
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "data.json")

with open(json_path, "r") as file:
    data = json.load(file)


# ---------- Convert to DataFrame ----------
df = pd.DataFrame(data)

# ---------- Convert date column ----------
df["businessDate"] = pd.to_datetime(df["businessDate"])

# ---------- Set date as index ----------
df.set_index("businessDate", inplace=True)

# ---------- Plot ----------
plt.figure(figsize=(10, 5))

plt.plot(df.index, df["marCap"], label="Market Cap")
plt.plot(df.index, df["floatMarCap"], label="Float Market Cap")
plt.plot(df.index, df["senMarCap"], label="Sensitive Market Cap")
plt.plot(df.index, df["senFloatMarCap"], label="Sensitive Float Market Cap")

plt.title("Market Capitalization Over Time")
plt.xlabel("Business Date")
plt.ylabel("Value")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("market_cap_chart.png", dpi=300)
print("Chart saved as market_cap_chart.png")
