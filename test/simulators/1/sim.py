import numpy as np
import pandas as pd
from tqdm import tqdm

def calculate_std_dev(row, config):
    ratio = config["pos_std_dev_ratios"].get(row["Position"], 0.3)
    return row["BaseProjection"] * ratio

def generate_simulations(df, config):
    num_simulations = config["num_simulations"]
    correlation_factor = config["correlation_factor"]
    player_usage = config["player_usage"]
    num_players_to_align = 5  # Now including RB
    alignment_counts = {
        "all_five": 0,
        "four_of_five": 0,
        "three_of_five": 0,
        "two_of_five": 0,
        "one_of_five": 0,
        "zero_of_five": 0,
    }

    simulation_results = []

    for _ in tqdm(range(num_simulations), desc="Simulating"):
        sim_result = {}
        qb_variance_dict = {}
        alignment_directions = []

        # Apply variance to QB
        for qb in df[df["Position"] == "QB"].itertuples():
            std_dev = qb.StdDev
            qb_variance = np.random.normal(0, std_dev)
            qb_adjusted_projection = qb.BaseProjection + qb_variance
            qb_variance_dict[qb.Team] = qb_variance * correlation_factor  # Scale QB variance
            sim_result[qb.Player] = max(0, qb_adjusted_projection)

        # Apply variance to other players
        for player in df[df["Position"] != "QB"].itertuples():
            team = player.Team
            position = player.Position
            base_projection = player.BaseProjection
            std_dev = player.StdDev
            independent_variance = np.random.normal(0, std_dev)

            # Teammate correlation adjustments
            if team in qb_variance_dict:
                qb_variance = qb_variance_dict[team]
                usage_factor = player_usage.get(position, 0.2)
                correlated_variance = qb_variance * usage_factor
                adjusted_projection = base_projection + correlated_variance + independent_variance
            else:
                adjusted_projection = base_projection + independent_variance

            sim_result[player.Player] = max(0, adjusted_projection)

            # Track WR, TE, and RB movements for QB
            if position in ["WR1", "WR2", "WR3", "TE", "RB"]:
                alignment_directions.append(np.sign(adjusted_projection - base_projection))

        # Count WR, TE, and RB alignment with QB
        if alignment_directions:
            qb_direction = np.sign(qb_variance_dict.get("Team_A", 0))
            aligned = [1 for dir_ in alignment_directions if dir_ == qb_direction]
            num_aligned = len(aligned)
            if num_aligned == 5:
                alignment_counts["all_five"] += 1
            elif num_aligned == 4:
                alignment_counts["four_of_five"] += 1
            elif num_aligned == 3:
                alignment_counts["three_of_five"] += 1
            elif num_aligned == 2:
                alignment_counts["two_of_five"] += 1
            elif num_aligned == 1:
                alignment_counts["one_of_five"] += 1
            else:
                alignment_counts["zero_of_five"] += 1

        simulation_results.append(sim_result)

    simulation_df = pd.DataFrame(simulation_results)
    return simulation_df, alignment_counts
import numpy as np
import pandas as pd
from tqdm import tqdm

def calculate_std_dev(row, config):
    ratio = config["pos_std_dev_ratios"].get(row["Position"], 0.3)
    return row["BaseProjection"] * ratio

def generate_simulations(df, config):
    num_simulations = config["num_simulations"]
    correlation_factor = config["correlation_factor"]
    player_usage = config["player_usage"]
    num_players_to_align = 5  # Now including RB
    alignment_counts = {
        "all_five": 0,
        "four_of_five": 0,
        "three_of_five": 0,
        "two_of_five": 0,
        "one_of_five": 0,
        "zero_of_five": 0,
    }

    simulation_results = []

    for _ in tqdm(range(num_simulations), desc="Simulating"):
        sim_result = {}
        qb_variance_dict = {}
        alignment_directions = []

        # Apply variance to QB
        for qb in df[df["Position"] == "QB"].itertuples():
            std_dev = qb.StdDev
            qb_variance = np.random.normal(0, std_dev)
            qb_adjusted_projection = qb.BaseProjection + qb_variance
            qb_variance_dict[qb.Team] = qb_variance * correlation_factor  # Scale QB variance
            sim_result[qb.Player] = max(0, qb_adjusted_projection)

        # Apply variance to other players
        for player in df[df["Position"] != "QB"].itertuples():
            team = player.Team
            position = player.Position
            base_projection = player.BaseProjection
            std_dev = player.StdDev
            independent_variance = np.random.normal(0, std_dev)

            # Teammate correlation adjustments
            if team in qb_variance_dict:
                qb_variance = qb_variance_dict[team]
                usage_factor = player_usage.get(position, 0.2)
                correlated_variance = qb_variance * usage_factor
                adjusted_projection = base_projection + correlated_variance + independent_variance
            else:
                adjusted_projection = base_projection + independent_variance

            sim_result[player.Player] = max(0, adjusted_projection)

            # Track WR, TE, and RB movements for QB
            if position in ["WR1", "WR2", "WR3", "TE", "RB"]:
                alignment_directions.append(np.sign(adjusted_projection - base_projection))

        # Count WR, TE, and RB alignment with QB
        if alignment_directions:
            qb_direction = np.sign(qb_variance_dict.get("Team_A", 0))
            aligned = [1 for dir_ in alignment_directions if dir_ == qb_direction]
            num_aligned = len(aligned)
            if num_aligned == 5:
                alignment_counts["all_five"] += 1
            elif num_aligned == 4:
                alignment_counts["four_of_five"] += 1
            elif num_aligned == 3:
                alignment_counts["three_of_five"] += 1
            elif num_aligned == 2:
                alignment_counts["two_of_five"] += 1
            elif num_aligned == 1:
                alignment_counts["one_of_five"] += 1
            else:
                alignment_counts["zero_of_five"] += 1

        simulation_results.append(sim_result)

    simulation_df = pd.DataFrame(simulation_results)
    return simulation_df, alignment_counts

