import pandas as pd
import os
import sys

# Ensure the script can find config.py by adjusting the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paths from the config file
from config import MATCHES_FULL, WIN_PROB_DIR

# Paths
matches_file_dir = MATCHES_FULL  # Directory where matches_full.csv is stored
win_prob_dir = WIN_PROB_DIR  # Directory to save the win probabilities file
win_prob_file_path = os.path.join(win_prob_dir, "win_prob.csv")

# Step 1: Load the matches_full Data
matches_file = next(f for f in os.listdir(matches_file_dir) if f.endswith('.csv'))
matches_file_path = os.path.join(matches_file_dir, matches_file)
matches_df = pd.read_csv(matches_file_path)

# Step 2: Ensure data is sorted by match_id and player_match_id
matches_df = matches_df.sort_values(by=['match_id', 'player_match_id'])

# Step 3: Perform Win Probability Calculation
def calculate_elo_win_probability(player_elo, opponent_elo):
    S = 400  # Standard scaling factor for ELO
    win_prob = 1 / (1 + 10 ** ((opponent_elo - player_elo) / S))
    return win_prob

# Initialize lists to store probabilities
elo_win_probs = []

# Iterate through each match and calculate win probabilities
for match_id in matches_df['match_id'].unique():
    match_data = matches_df[matches_df['match_id'] == match_id]
    
    if len(match_data) == 2:  # Ensure there are exactly 2 rows for each match
        player1_elo = match_data.iloc[0]['surface_elo']
        player2_elo = match_data.iloc[1]['surface_elo']
        
        # Calculate win probabilities
        player1_win_prob = calculate_elo_win_probability(player1_elo, player2_elo)
        player2_win_prob = 1 - player1_win_prob
        
        # Append probabilities to the list, formatted to 3 decimal places
        elo_win_probs.append(f"{player1_win_prob:.3f}")
        elo_win_probs.append(f"{player2_win_prob:.3f}")
    else:
        elo_win_probs.extend([None, None])

# Add the formatted probabilities to the DataFrame as 'elo_win_prob'
matches_df['elo_win_prob'] = elo_win_probs

# Step 4: Filter out matches without calculated win probabilities
matches_df = matches_df.dropna(subset=['elo_win_prob'])

# Step 5: Drop unwanted columns
matches_df = matches_df.drop(columns=['moneyline_odds_american', 'Tour', 'surface_elo', 'opponent_win_prob'], errors='ignore')

# Step 6: Ensure the win_prob directory exists
os.makedirs(win_prob_dir, exist_ok=True)

# Step 7: Save the win_prob.csv
matches_df.to_csv(win_prob_file_path, index=False)
print(f"Filtered matches with calculated elo_win_prob saved to {win_prob_file_path}")

