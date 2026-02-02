import pandas as pd

file_path = "stock/1901522e5b7428bf3c331b51de40378e.xlsx"

xls = pd.ExcelFile(file_path)

print("Number of sheets:", len(xls.sheet_names))
print("Sheet names:")
for name in xls.sheet_names:
    print("-", name)
