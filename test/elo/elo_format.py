import os
import pandas as pd
import numpy as np
import sys

# Ensure the script can find config.py by adjusting the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paths from config
from config import RAW_ELO, PROC_ELO

def load_data(elo_path, yelo_path):
    """
    Load ELO and yELO data from the provided file paths.
    """
    elo_df = pd.read_csv(elo_path)
    yelo_df = pd.read_csv(yelo_path)
    return elo_df, yelo_df

def scale_yelo_to_elo(yelo_df, elo_df, top_percentile=95, bottom_percentile=5):
    """
    Scale yElo values using mean and standard deviation for the bulk of the data,
    and apply additional scaling for the top and bottom percentiles.
    """
    # Standard Scaling: Mean and Standard Deviation
    mean_elo = elo_df['Elo'].mean()
    std_elo = elo_df['Elo'].std()
    
    mean_yelo = yelo_df['yElo'].mean()
    std_yelo = yelo_df['yElo'].std()

    yelo_df['Scaled yElo'] = (yelo_df['yElo'] - mean_yelo) / std_yelo * std_elo + mean_elo

    # Percentile Scaling: Top and Bottom Percentiles
    top_yelo_value = np.percentile(yelo_df['yElo'], top_percentile)
    top_elo_value = np.percentile(elo_df['Elo'], top_percentile)

    bottom_yelo_value = np.percentile(yelo_df['yElo'], bottom_percentile)
    bottom_elo_value = np.percentile(elo_df['Elo'], bottom_percentile)

    # Apply scaling adjustments to the top and bottom percentiles
    yelo_df['Scaled yElo'] = yelo_df.apply(lambda row: 
                                           row['Scaled yElo'] * (top_elo_value / top_yelo_value) if row['yElo'] >= top_yelo_value else
                                           row['Scaled yElo'] * (bottom_elo_value / bottom_yelo_value) if row['yElo'] <= bottom_yelo_value else
                                           row['Scaled yElo'], axis=1)

    return yelo_df

def apply_age_adjustment(row):
    """
    Adjust yELO based on the player's age relative to the prime age range (24-28).
    """
    age = row['Age']
    adjusted_yelo = row['Scaled yElo']
    factor = 5  # Adjustment factor, tweak as needed
    
    if age < 24:
        adjusted_yelo += factor * (24 - age)
    elif age > 28:
        adjusted_yelo -= factor * (age - 28)
    
    return adjusted_yelo

def calculate_weighted_average(row):
    """
    Calculate the weighted average of ELO and yELO based on the number of matches played.
    """
    matches = row['Total Matches']
    elo = row['Elo']
    yelo = row['Adjusted yELO']
    
    if matches <= 20:
        weight_elo = 0.8
        weight_yelo = 0.2
    elif matches >= 50:
        weight_elo = 0.4
        weight_yelo = 0.6
    else:
        # Linear interpolation between 21 and 49 matches
        weight_yelo = 0.2 + ((matches - 20) / 30) * 0.4
        weight_elo = 1 - weight_yelo
    
    return (elo * weight_elo) + (yelo * weight_yelo)

def combine_elo_yelo(elo_df, yelo_df, tour):
    """
    Combine ELO and scaled yELO data, apply age adjustments, calculate the weighted average,
    and add a column to specify if the player is WTA or ATP.
    """
    yelo_df['Total Matches'] = yelo_df['Wins'] + yelo_df['Losses']
    
    # Merge ELO and yELO data
    combined_df = pd.merge(
        elo_df[['Player', 'Elo', 'Age', 'HardRaw', 'ClayRaw', 'GrassRaw']],
        yelo_df[['Player', 'Scaled yElo', 'Total Matches']],
        on='Player',
        how='inner'
    )
    
    # Apply age adjustments to yELO
    combined_df['Adjusted yELO'] = combined_df.apply(apply_age_adjustment, axis=1)
    
    # Calculate the weighted average
    combined_df['Weighted Average'] = combined_df.apply(calculate_weighted_average, axis=1)
    
    # Add a column to specify if the player is WTA or ATP
    combined_df['Tour'] = tour
    
    # Return the final DataFrame with the necessary columns
    return combined_df[['Player', 'Weighted Average', 'HardRaw', 'ClayRaw', 'GrassRaw', 'Tour']]

def save_to_csv(df, output_path):
    """
    Save the final DataFrame to a CSV file.
    """
    df.to_csv(output_path, index=False)
    print(f"Saved final DataFrame to {output_path}")

if __name__ == "__main__":
    # ATP paths
    atp_elo_path = os.path.join(RAW_ELO, "atpelo.csv")
    atp_yelo_path = os.path.join(RAW_ELO, "atpyelo.csv")
    
    # WTA paths
    wta_elo_path = os.path.join(RAW_ELO, "wtaelo.csv")
    wta_yelo_path = os.path.join(RAW_ELO, "wtayelo.csv")
    
    # Load data
    atp_elo_df, atp_yelo_df = load_data(atp_elo_path, atp_yelo_path)
    wta_elo_df, wta_yelo_df = load_data(wta_elo_path, wta_yelo_path)
    
    # Scale yELO to match ELO
    atp_yelo_df = scale_yelo_to_elo(atp_yelo_df, atp_elo_df)
    wta_yelo_df = scale_yelo_to_elo(wta_yelo_df, wta_elo_df)
    
    # Combine ELO and scaled yELO data, apply age adjustments, and calculate the weighted average
    atp_final_df = combine_elo_yelo(atp_elo_df, atp_yelo_df, "ATP")
    wta_final_df = combine_elo_yelo(wta_elo_df, wta_yelo_df, "WTA")
    
    # Combine both ATP and WTA into a single DataFrame
    combined_df = pd.concat([atp_final_df, wta_final_df], ignore_index=True)
    
    # Save the final combined DataFrame to a CSV file in the processed directory
    output_file_path = os.path.join(PROC_ELO, "combined_weighted_elo_adjusted.csv")
    save_to_csv(combined_df, output_file_path)

