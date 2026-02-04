# import pandas as pd

# file_path = "stock/1901522e5b7428bf3c331b51de40378e.xlsx"

# xls = pd.ExcelFile(file_path)

# print("Number of sheets:", len(xls.sheet_names))
# print("Sheet names:")
# for name in xls.sheet_names:
#     print("-", name)






import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime


# --------- helper to avoid overwriting files ----------
def get_unique_filename(base_name, ext=".png", out_dir="."):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(out_dir, f"{base_name}_{timestamp}{ext}")


# --------- read Excel data ----------
file_path = "stock/1901522e5b7428bf3c331b51de40378e.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="Brokerwise Trading Amount",
    header=7,
    usecols=[0, 1, 2]
)

df.columns = ["member", "buy", "sell"]
df = df.dropna(how="all")

# --------- calculate net percentage ----------
df["total"] = df["buy"] + df["sell"]
df = df[df["total"] > 0]  # safety

df["net_pct"] = ((df["buy"] - df["sell"]) / df["total"]) * 100

# --------- select TOP 10 by absolute % difference ----------
df = df.reindex(df["net_pct"].abs().sort_values(ascending=False).index)
df = df.head(10)

# --------- print data ----------
pd.options.display.float_format = "{:.2f}".format

print("\nTop 10 Brokers by Net Trading Percentage:\n")
print(df[["member", "net_pct"]].to_string(index=False))
print("\nRows:", len(df))


# --------- horizontal double bar chart ----------
y = np.arange(len(df))

net_buy_pct = df["net_pct"].clip(lower=0)
net_sell_pct = df["net_pct"].clip(upper=0)

plt.figure(figsize=(12, 6))

plt.barh(y, net_buy_pct, label="Net Buy %")
plt.barh(y, net_sell_pct, label="Net Sell %")

plt.yticks(y, df["member"])
plt.xlabel("Net Trading Percentage (%)")
plt.title("Top 10 Brokers by Net Buy/Sell Percentage")
plt.axvline(0)

plt.legend()
plt.tight_layout()

# --------- save ----------
output_file = get_unique_filename("Broker_Net_Percentage")
plt.savefig(output_file, dpi=300)
print(f"\nChart saved as {output_file}")

plt.show()
