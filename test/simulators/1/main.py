import numpy as np
import pandas as pd
from sim import calculate_std_dev, generate_simulations

# Configuration
CONFIG = {
    "num_simulations": 10000,
    "pos_std_dev_ratios": {
        "QB": 0.30,
        "RB": 0.40,
        "WR1": 0.40,
        "WR2": 0.35,
        "WR3": 0.30,
        "TE": 0.35,
        "DST": 0.25,
    },
    "player_usage": {
        "WR1": 0.35,
        "WR2": 0.25,
        "WR3": 0.15,
        "TE": 0.15,
        "RB": 0.2,
    },
    "correlation_factor": 2,  # Tune this (higher = stronger teammate correlation)
}

# Player Data
df_players = pd.DataFrame([
    {"Player": "QB_Team_A", "Position": "QB", "Team": "Team_A", "BaseProjection": 20},
    {"Player": "WR1_Team_A", "Position": "WR1", "Team": "Team_A", "BaseProjection": 18},
    {"Player": "WR2_Team_A", "Position": "WR2", "Team": "Team_A", "BaseProjection": 15},
    {"Player": "WR3_Team_A", "Position": "WR3", "Team": "Team_A", "BaseProjection": 12},
    {"Player": "TE_Team_A", "Position": "TE", "Team": "Team_A", "BaseProjection": 10},
    {"Player": "RB_Team_A", "Position": "RB", "Team": "Team_A", "BaseProjection": 16},
    {"Player": "DST_Team_A", "Position": "DST", "Team": "Team_A", "BaseProjection": 8},
])

# Calculate Standard Deviations
df_players["StdDev"] = df_players.apply(calculate_std_dev, axis=1, args=(CONFIG,))

# Run simulations
simulation_df, alignment_counts = generate_simulations(df_players, CONFIG)

# Calculate summary statistics
summary_stats = simulation_df.describe(percentiles=[0.25, 0.5, 0.75, 0.85, 0.95, 0.99]).T
summary_stats = summary_stats[["mean", "25%", "50%", "75%", "85%", "95%", "99%"]]
summary_stats.columns = ["Mean", "P25", "P50", "P75", "P85", "P95", "P99"]

# Merge with base projections
summary_stats = summary_stats.merge(df_players[["Player", "BaseProjection"]], left_index=True, right_on="Player")

# Calculate correlations with QB for each position, including RB
correlation_df = simulation_df.corr()

positions = ["WR1", "WR2", "WR3", "TE", "RB", "DST"]
correlations_with_qb = {}
for position in positions:
    player_name = f"{position}_Team_A"
    if player_name in correlation_df.columns:
        correlations_with_qb[f"{position}-QB_Team_A"] = correlation_df.loc[player_name, "QB_Team_A"]

# Display results
print("\nPlayer Simulation Results:")
print(summary_stats)

print("\nPlayer Correlations with QB:")
for key, value in correlations_with_qb.items():
    print(f"{key}: Corr = {value:.2f}")

# Display alignment results
total_simulations = CONFIG["num_simulations"]
print("\nWR, TE & RB Alignment Results:")
print(f"All five skill positions aligned with QB: {alignment_counts['all_five'] / total_simulations:.2%}")
print(f"Four of five skill positions aligned with QB: {alignment_counts['four_of_five'] / total_simulations:.2%}")
print(f"Three of five skill positions aligned with QB: {alignment_counts['three_of_five'] / total_simulations:.2%}")
print(f"Two of five skill positions aligned with QB: {alignment_counts['two_of_five'] / total_simulations:.2%}")
print(f"One of five skill positions aligned with QB: {alignment_counts['one_of_five'] / total_simulations:.2%}")
print(f"Zero of five skill positions aligned with QB: {alignment_counts['zero_of_five'] / total_simulations:.2%}")

# Display team total projections
for team in df_players["Team"].unique():
    team_players = df_players[df_players["Team"] == team]["Player"].tolist()
    team_totals = simulation_df[team_players].sum(axis=1)
    team_summary = team_totals.describe(percentiles=[0.25, 0.5, 0.75, 0.85, 0.95, 0.99])
    print(f"\n{team} Total Fantasy Points Summary:")
    print(team_summary[["mean", "25%", "50%", "75%", "85%", "95%", "99%"]])

