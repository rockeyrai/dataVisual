import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
SALTER_TOKEN = "Salter eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..rHbAGHTGa_JAdbR4Nh_8fg.lVKejZDpqV_CjQPkN3KA_1HptvfXOn9KogD_3zggCdLnhHGRZiWsWEE5jW4y_Wd66qLaWRSyE0QylyvUiCWcZh4cVpZD9se_nw3g1X8DuEyiBc7oUVQevXC8mBjER989WAZ3XKamZa1zQVkm-t7tYg.DIaJUZCF0jlJLX7sAyi06w"
BASE_URL = "https://www.nepalstock.com/api/nots/sectorwise"
DEFAULT_START_DATE = datetime(2025, 2, 2)
END_DATE = datetime(2026, 2, 1)
OUTPUT_FILE = "nepse_sector_data.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Authorization": SALTER_TOKEN,
    "Referer": "https://www.nepalstock.com/sector-summary",
}

def get_last_scraped_date():
    """Checks the CSV file and returns the last business_date found."""
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE)
            if not df_existing.empty:
                # Get the last date from the 'business_date' column
                last_date_str = df_existing['business_date'].iloc[-1]
                return datetime.strptime(last_date_str, "%Y-%m-%d")
        except Exception as e:
            print(f"⚠️ Error reading existing file: {e}")
    return None

def get_sector_data():
    # 1. Determine the actual start date
    last_date = get_last_scraped_date()
    if last_date:
        start_from = last_date + timedelta(days=1)
        print(f"📂 Found existing data. Resuming from: {start_from.date()}")
    else:
        start_from = DEFAULT_START_DATE
        print(f"🆕 No existing file found. Starting fresh from: {start_from.date()}")

    current_date = start_from
    
    while current_date <= END_DATE:
        if current_date.weekday() in [4, 5]:  # Skip Fri/Sat
            current_date += timedelta(days=1)
            continue

        formatted_date = current_date.strftime("%Y-%m-%d")
        params = {"businessDate": formatted_date}

        try:
            response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    new_df = pd.DataFrame(data)
                    new_df['business_date'] = formatted_date
                    
                    # 2. Save incrementally (Append mode)
                    file_exists = os.path.isfile(OUTPUT_FILE)
                    new_df.to_csv(OUTPUT_FILE, mode='a', index=False, header=not file_exists)
                    
                    print(f"✅ Fetched and Appended: {formatted_date}")
                else:
                    print(f"⚪ No data for {formatted_date} (Holiday)")
            elif response.status_code == 401:
                print(f"❌ 401 Unauthorized! Update your SALTER_TOKEN.")
                break
            else:
                print(f"❌ Error {response.status_code} for {formatted_date}")

        except Exception as e:
            print(f"⚠️ Connection error on {formatted_date}: {e}")

        time.sleep(1.5)  # Slightly longer delay to keep the connection stable
        current_date += timedelta(days=1)

    print(f"\n✨ Scraping session finished.")

if __name__ == "__main__":
    get_sector_data()