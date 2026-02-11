import pandas as pd
import numpy as np
import nepali_datetime
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SECTORS_TO_COMPARE = [
    # "NEPSE",
    "Banking",
    "Hydro Power",
    # "Development Bank",
    # "Finance",
    # "Life Insurance",
    # "Non-Life Insurance",
    # "Microfinance",
    "Hotels and Tourism",
    "Manufacturing and Processing",
    # "Trading",
    # "Investment",
    # "Mutual Fund",
]

def normalize_base_100(df, columns, base_date=None):
    """
    Normalize given columns to Base = 100
    """
    norm_df = df.copy()

    if base_date is None:
        base_date = norm_df["Date"].min()

    base_row = norm_df[norm_df["Date"] == base_date]

    if base_row.empty:
        return norm_df

    for col in columns:
        if col not in norm_df.columns:
            continue

        base_value = base_row[col].values[0]

        if pd.isna(base_value) or base_value == 0:
            continue

        norm_df[col] = (norm_df[col] / base_value) * 100

    return norm_df

# Finance Minister events
fm_events = pd.DataFrame({
    "Date": [
        "2018-03-16",
        "2020-10-14",
        "2021-07-13",
        "2022-12-26",
        "2023-03-31",
        "2024-03-06",
        "2024-07-15",
        "2025-09-15",
    ],
    "Finance Minister": [
        "Yuba Raj Khatiwada",
        "Bishnu Prasad Paudel",
        "Janardan Sharma",
        "Bishnu Prasad Paudel",
        "Prakash Sharan Mahat",
        "Barsaman Pun",
        "Bishnu Prasad Paudel",
        "Rameshwor Khanal",
    ]
})

fm_events["Date"] = pd.to_datetime(fm_events["Date"])

event_files = [
    "2074chaitra2.xlsx",
    "2077asoj28.xlsx",
    "2078ashar28.xlsx",
    "2079chaitra17.xlsx",
    "2079poush11.xlsx",
    "2080chaitra3.xlsx",
    "2081ashar31.xlsx",
    "2082bhadra30.xlsx",
]

STANDARD_MAP = {
    "date": "Date",
    "business_date": "Date",

    "banking": "Banking",
    "banking sub-index": "Banking",
    "banking subindex": "Banking",

    "hotels": "Hotels and Tourism",
    "hotels index": "Hotels and Tourism",
    "hotels and tourism index": "Hotels and Tourism",
    "hotels and tourism": "Hotels and Tourism",

    "others": "Others",
    "other index": "Others",
    "others index": "Others",

    "hydropower index": "Hydro Power",
    "hydro power": "Hydro Power",

    "development bank index": "Development Bank",
    "development bank": "Development Bank",

    "manufacturing and processing": "Manufacturing and Processing",
    "manufacturing and processing index": "Manufacturing and Processing",

    "microfinance index": "Microfinance",
    "micro-finance": "Microfinance",

    "life insurance": "Life Insurance",
    "life insurance index": "Life Insurance",

    "non life insurance": "Non-Life Insurance",
    "non-life insurance": "Non-Life Insurance",
    "non-life insurance index": "Non-Life Insurance",

    "finance index": "Finance",
    "trading index": "Trading",

    "float index": "Float",
    "sensitive float index": "Sensitive Float",
    "sensitive index": "Sensitive",
    "nepse index": "NEPSE",
    "Nepse": "NEPSE",
    "nepse": "NEPSE",


    "mutual fund": "Mutual Fund",
    "mutual fund index": "Mutual Fund",
    "investment index": "Investment"
}

def normalize_columns(df):
    clean_cols = []
    for col in df.columns:
        c = col.lower().replace("\n", " ").strip()
        c = " ".join(c.split())
        clean_cols.append(STANDARD_MAP.get(c, col))
    df.columns = clean_cols
    return df

def parse_mixed_date(value):
    if pd.isna(value):
        return pd.NaT

    # --- Excel serial numbers ---
    # if isinstance(value, (int, float)):
    #     # Excel serials representing BS dates should NOT be treated as AD
    #     if value < 40000:
    #         return pd.NaT  # force manual inspection / skip
    #     try:
    #         dt = pd.to_datetime(value, origin="1899-12-30", unit="D")
    #         if dt.year < 1990:
    #             return pd.NaT
    #         return dt
    #     except Exception:
    #         return pd.NaT

    value = str(value).strip()

    # --- BS string dates (2078/01/05, 2078-1-5) ---
    bs_match = re.match(r"^(20\d{2})[/-](\d{1,2})[/-](\d{1,2})$", value)
    if bs_match:
        try:
            y, m, d = map(int, bs_match.groups())
            if 2070 <= y <= 2090:
                bs_date = nepali_datetime.date(y, m, d)
                return pd.to_datetime(bs_date.to_datetime_date())
        except Exception:
            return pd.NaT

    # --- AD parsing ---
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return pd.NaT
        if dt.year < 1990 or dt.year > 2035:
            return pd.NaT
        return dt
    except Exception:
        return pd.NaT


def normalize_date_column(df):
    if "Date" not in df.columns:
        return df

    df["Date"] = df["Date"].apply(parse_mixed_date)
    return df

def create_fm_impact_graph(file_name, df, fm_events, output_dir):
    """
    Create a normalized (Base 100) graph comparing sector reactions
    """
    df = df[df["Date"].notna()].copy()
    df = df.sort_values("Date")

    if len(df) == 0:
        print(f"⚠️  No valid data for {file_name}")
        return

    # Find available sectors in this file
    available_sectors = [s for s in SECTORS_TO_COMPARE if s in df.columns]

    if len(available_sectors) < 2:
        print(f"⚠️  Not enough sector data in {file_name}")
        return

    # Normalize to Base 100
    df_norm = normalize_base_100(df, available_sectors)

    min_date = df_norm["Date"].min()
    max_date = df_norm["Date"].max()

    print(f"\n📊 Processing {file_name}")
    print(f"   Date range: {min_date.date()} → {max_date.date()}")
    print(f"   Sectors compared: {available_sectors}")

    relevant_fm_events = fm_events[
        (fm_events["Date"] >= min_date) &
        (fm_events["Date"] <= max_date)
    ]

    fig, ax = plt.subplots(figsize=(16, 9))

    # Plot normalized sectors
    for sector in available_sectors:
        ax.plot(
            df_norm["Date"],
            df_norm[sector],
            linewidth=2,
            alpha=0.9,
            label=sector
        )

    # Finance Minister event lines
    for _, row in relevant_fm_events.iterrows():
        ax.axvline(
            x=row["Date"],
            linestyle="--",
            linewidth=2,
            color="black",
            alpha=0.6
        )

        ax.text(
            row["Date"],
            ax.get_ylim()[1],
            f"{row['Finance Minister']}\n{row['Date'].strftime('%Y-%m-%d')}",
            rotation=90,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8)
        )

    ax.set_title(
        f"Sectoral Reaction to Finance Minister Change (Base = 100)\n{file_name}",
        fontsize=15,
        weight="bold"
    )
    ax.set_xlabel("Date", fontsize=12, weight="bold")
    ax.set_ylabel("Index (Base = 100)", fontsize=12, weight="bold")

    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="upper left", fontsize=10, ncol=2)

    plt.xticks(rotation=45)
    plt.subplots_adjust(right=0.95)

    output_path = output_dir / f"{file_name.replace('.xlsx', '_sector_base100.png')}"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"✅ Generated: {output_path}")

def main():
    # Create output directory
    output_dir = BASE_DIR / "fm_impact_graphs"
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Generating Finance Minister Impact Graphs")
    print("=" * 60)
    
    for file_name in event_files:
        file_path = BASE_DIR / file_name
        
        try:
            # Read and process data
            df = pd.read_excel(file_path, sheet_name="index")
            df = normalize_columns(df)
            df = normalize_date_column(df)
            
            # Create graph
            create_fm_impact_graph(file_name, df, fm_events, output_dir)
            
        except Exception as e:
            print(f"\n❌ Error processing {file_name}:")
            print(f"   {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print(f"All graphs saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()