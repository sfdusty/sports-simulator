import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import sys

# Ensure the script can find config.py by adjusting the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the RAW_ELO path from the config file
from config import RAW_ELO

def normalize_name(name):
    # Normalize by removing non-breaking spaces and stripping extra spaces
    return name.replace('\xa0', ' ').strip().lower()

def fetch_elo_ratings(url):
    # Create a UserAgent object to generate random User-Agent headers
    ua = UserAgent()

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Referer": "http://tennisabstract.com/",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br, zstd"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table', id='reportable')

        if table:
            # Extract headers
            headers = [th.text.strip() for th in table.find_all('th')]

            # Extract rows
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = tr.find_all('td')
                row = [cell.text.strip() for cell in cells]
                rows.append(row)

            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)

            # Normalize player names
            df['Player'] = df['Player'].apply(normalize_name)

            # Check and replace Leylah Fernandez with Leylah Annie Fernandez
            df['Player'] = df['Player'].replace('leylah fernandez', 'leylah annie fernandez')

            return df
    return pd.DataFrame()  # Return an empty DataFrame if there's an issue

def filter_and_save_elo_data(elo_df, yelo_df, output_path):
    # Filter out players not in yELO
    filtered_df = elo_df[elo_df['Player'].isin(yelo_df['Player'])]

    # Save the filtered DataFrame to the specified path
    filtered_df.to_csv(output_path, index=False)
    print(f"Saved filtered data to {output_path}")

# Ensure the RAW_ELO directory exists
os.makedirs(RAW_ELO, exist_ok=True)

# URLs to scrape
urls = {
    "ATP Elo": "https://www.tennisabstract.com/reports/atp_elo_ratings.html",
    "WTA Elo": "https://www.tennisabstract.com/reports/wta_elo_ratings.html",
    "ATP yElo": "http://tennisabstract.com/reports/atp_season_yelo_ratings.html",
    "WTA yElo": "http://tennisabstract.com/reports/wta_season_yelo_ratings.html"
}

# Fetch ELO and yELO data
print("Fetching ATP Elo data...")
atp_elo_df = fetch_elo_ratings(urls["ATP Elo"])

print("Fetching ATP yElo data...")
atp_yelo_df = fetch_elo_ratings(urls["ATP yElo"])

print("Fetching WTA Elo data...")
wta_elo_df = fetch_elo_ratings(urls["WTA Elo"])

print("Fetching WTA yElo data...")
wta_yelo_df = fetch_elo_ratings(urls["WTA yElo"])

# Filter and save ATP Elo data
print("\nSaving ATP Elo data...")
filter_and_save_elo_data(atp_elo_df, atp_yelo_df, os.path.join(RAW_ELO, "atpelo.csv"))

# Filter and save ATP yElo data
print("Saving ATP yElo data...")
filter_and_save_elo_data(atp_yelo_df, atp_yelo_df, os.path.join(RAW_ELO, "atpyelo.csv"))

# Filter and save WTA Elo data
print("Saving WTA Elo data...")
filter_and_save_elo_data(wta_elo_df, wta_yelo_df, os.path.join(RAW_ELO, "wtaelo.csv"))

# Filter and save WTA yElo data
print("Saving WTA yElo data...")
filter_and_save_elo_data(wta_yelo_df, wta_yelo_df, os.path.join(RAW_ELO, "wtayelo.csv"))

