import os
import sys
import pandas as pd

# Ensure the script can find config.py by adjusting the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paths from the config file
from config import PREPPED_ODDS_DIR, PROC_ELO, MATCHES_FULL

def normalize_name(name):
    # Normalize by removing non-breaking spaces and stripping extra spaces
    return name.replace('\xa0', ' ').strip().lower()

def get_newest_file(directory):
    """
    Get the newest file in a directory.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def select_surface_elo(row):
    """
    Select the appropriate ELO rating based on the surface.
    """
    if row['surface'] == 'hard':
        return row['Hard']
    elif row['surface'] == 'clay':
        return row['Clay']
    elif row['surface'] == 'grass':
        return row['Grass']
    return None

def merge_dataframes(prepped_file_path, elo_file_path):
    """
    Load the prepped odds and processed ELO data, then merge them on the player name.
    """
    # Load the data
    prepped_df = pd.read_csv(prepped_file_path)
    elo_df = pd.read_csv(elo_file_path)
    
    # Normalize the player names in both DataFrames
    prepped_df['player'] = prepped_df['player'].apply(normalize_name)
    elo_df['Player'] = elo_df['Player'].apply(normalize_name)
    
    # Merge the dataframes on the player columns
    merged_df = pd.merge(prepped_df, elo_df, left_on='player', right_on='Player', how='left')
    
    # Select the appropriate surface ELO rating
    merged_df['surface_elo'] = merged_df.apply(select_surface_elo, axis=1)
    
    # Drop the individual surface columns and the 'Player' column from the ELO data
    merged_df = merged_df.drop(columns=['Hard', 'Clay', 'Grass', 'Player'])
    
    return merged_df

def save_to_matches_full(df, directory):
    """
    Save the merged DataFrame to the matches_full directory.
    """
    os.makedirs(directory, exist_ok=True)
    output_path = os.path.join(directory, "matches_full.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved merged DataFrame to {output_path}")

if __name__ == "__main__":
    # Get the newest files from the directories
    prepped_file = get_newest_file(PREPPED_ODDS_DIR)
    if prepped_file is None:
        print("No prepped odds file found.")
        sys.exit(1)

    elo_file = get_newest_file(PROC_ELO)
    if elo_file is None:
        print("No processed ELO file found.")
        sys.exit(1)

    # Merge the dataframes
    merged_df = merge_dataframes(prepped_file, elo_file)
    
    # Save the merged DataFrame to the matches_full directory
    save_to_matches_full(merged_df, MATCHES_FULL)
    
    # Display the full merged dataframe in the terminal (optional)
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    print(merged_df.to_string())  # Display the full DataFrame

