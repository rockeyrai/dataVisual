import pandas as pd
import numpy as np
import nepali_datetime
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

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
    Create a graph showing NEPSE index with Finance Minister change events
    """
    # Filter valid dates
    df = df[df["Date"].notna()].copy()
    df = df.sort_values("Date")
    
    if len(df) == 0:
        print(f"⚠️  No valid data for {file_name}")
        return
    
    # Check if NEPSE column exists
    if "NEPSE" not in df.columns:
        print(f"⚠️  No NEPSE column found in {file_name}")
        print(f"   Available columns: {list(df.columns)}")
        return
    
    # Filter NEPSE data
    nepse_data = df[["Date", "NEPSE"]].dropna()
    
    if len(nepse_data) == 0:
        print(f"⚠️  No valid NEPSE data for {file_name}")
        return
    
    # Get date range from data
    min_date = nepse_data["Date"].min()
    max_date = nepse_data["Date"].max()
    
    print(f"\n📊 Processing {file_name}")
    print(f"   Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"   NEPSE data points: {len(nepse_data)}")
    
    # Filter FM events to those within the data range
    relevant_fm_events = fm_events[
        (fm_events["Date"] >= min_date) & 
        (fm_events["Date"] <= max_date)
    ]
    
    print(f"   FM events in range: {len(relevant_fm_events)}")
    for _, event in relevant_fm_events.iterrows():
        print(f"      - {event['Date'].strftime('%Y-%m-%d')}: {event['Finance Minister']}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Plot NEPSE index
    ax.plot(nepse_data["Date"], nepse_data["NEPSE"], 
           linewidth=2.5, color="#1f77b4", label="NEPSE Index", alpha=0.9)
    
    # Add vertical lines for FM events with side labels
    event_colors = ['#FF0000', '#FF4500', '#DC143C', '#B22222', '#8B0000']
    
    for idx, (_, row) in enumerate(relevant_fm_events.iterrows()):
        event_date = row["Date"]
        fm_name = row["Finance Minister"]
        
        color = event_colors[idx % len(event_colors)]
        
        # Draw vertical line
        ax.axvline(x=event_date, color=color, linestyle='--', linewidth=2.5, alpha=0.7)
        
        # Add label on the right side
        ylim = ax.get_ylim()
        y_range = ylim[1] - ylim[0]
        
        # Stagger labels vertically to avoid overlap
        y_offset = ylim[1] - (idx * y_range * 0.15)
        
        # Add text on the right side
        ax.text(1.01, y_offset / ylim[1], 
               f"📅 {event_date.strftime('%Y-%m-%d')}\n{fm_name}", 
               transform=ax.get_yaxis_transform(),
               fontsize=10, color=color, weight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=color, alpha=0.9, linewidth=2))
    
    # Formatting
    ax.set_xlabel("Date", fontsize=13, weight='bold')
    ax.set_ylabel("NEPSE Index Value", fontsize=13, weight='bold')
    ax.set_title(f"Finance Minister Impact on NEPSE Index\n{file_name}", 
                fontsize=15, weight='bold', pad=20)
    
    # Format x-axis dates based on date range
    date_range_days = (max_date - min_date).days
    
    if date_range_days < 90:  # Less than 3 months
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    elif date_range_days < 365:  # Less than 1 year
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    else:  # More than 1 year
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    
    # Legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Adjust layout to make room for right-side labels
    plt.subplots_adjust(right=0.78)
    
    # Save figure
    output_path = output_dir / f"{file_name.replace('.xlsx', '_nepse_impact.png')}"
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