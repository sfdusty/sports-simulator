import pandas as pd
import numpy as np
import os
import json
import sys

# Ensure the script can find config.py by adjusting the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paths from config
from config import PROC_ELO, ELO_WEIGHTS

def load_weights(json_path):
    """
    Load the weighting structure from the JSON file.
    """
    with open(json_path, 'r') as file:
        weights = json.load(file)
    return weights

def calculate_surface_elo(row, weights):
    """
    Calculate surface-specific ELO ratings using the weighting structure from the JSON file.
    """
    tour = row['Tour']
    weighted_avg = row['Weighted Average']
    
    # Load the appropriate weights
    hard_weight = weights[tour]['Hard']
    clay_weight = weights[tour]['Clay']
    grass_weight = weights[tour]['Grass']
    
    # Convert to numeric, forcing errors to NaN, so we can safely use np.isnan
    hard_raw = pd.to_numeric(row['HardRaw'], errors='coerce')
    clay_raw = pd.to_numeric(row['ClayRaw'], errors='coerce')
    grass_raw = pd.to_numeric(row['GrassRaw'], errors='coerce')
    
    # Calculate surface-specific ELOs using the weighted structure
    hard_elo = (weighted_avg * hard_weight['enhanced'] + hard_raw * hard_weight['surface']) if not np.isnan(hard_raw) else weighted_avg
    clay_elo = (weighted_avg * clay_weight['enhanced'] + clay_raw * clay_weight['surface']) if not np.isnan(clay_raw) else weighted_avg
    grass_elo = (weighted_avg * grass_weight['enhanced'] + grass_raw * grass_weight['surface']) if not np.isnan(grass_raw) else weighted_avg
    
    return hard_elo, clay_elo, grass_elo

def create_surface_elos_df(df, weights):
    """
    Apply the surface-specific ELO calculation to the entire DataFrame using the weights.
    """
    # Calculate surface-specific ELOs for each player
    df[['Hard', 'Clay', 'Grass']] = df.apply(lambda row: calculate_surface_elo(row, weights), axis=1, result_type='expand')
    
    # Return only the Player and their surface-specific ELOs
    return df[['Player', 'Tour', 'Hard', 'Clay', 'Grass']]

def save_to_csv(df, output_path):
    """
    Save the final DataFrame with surface-specific ELOs to a CSV file.
    """
    df.to_csv(output_path, index=False)
    print(f"Saved surface-specific ELOs to {output_path}")

def delete_input_file(file_path):
    """
    Delete the input file after processing.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted input file {file_path}")

def get_newest_file(directory):
    """
    Get the newest file in a directory.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

if __name__ == "__main__":
    # Get the newest file from the PROC_ELO directory
    input_file_path = get_newest_file(PROC_ELO)
    if input_file_path is None:
        print("No files found in the PROC_ELO directory.")
        sys.exit(1)

    # Define the output path in the same directory
    output_file_path = os.path.join(PROC_ELO, "prepped_elo.csv")
    
    # Load the weighting structure
    weights = load_weights(ELO_WEIGHTS)
    
    # Load the combined weighted ELO DataFrame
    df = pd.read_csv(input_file_path)
    
    # Create the surface-specific ELO DataFrame
    surface_elos_df = create_surface_elos_df(df, weights)
    
    # Save the surface-specific ELOs to a CSV file
    save_to_csv(surface_elos_df, output_file_path)
    
    # Delete the input file after processing
    delete_input_file(input_file_path)

