import requests
import csv
import os
from datetime import datetime

API_KEY = 'Your_API_Key_Here'
tennis_sport_code = 'NAS'
output_dir = '/home/ds/ten/data/raw/dk'
log_dir = '/home/ds/ten/data/logs/dk'
log_file_path = os.path.join(log_dir, 'scrape_log.txt')

def get_contests(sport_code):
    url = f"https://www.draftkings.com/lobby/getcontests?sport={sport_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_player_pool(draft_group_id):
    url = f"https://api.draftkings.com/draftgroups/v1/draftgroups/{draft_group_id}/draftables?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def generate_file_path(base_path, date_str, index):
    filename = f"{tennis_sport_code}_{date_str}"
    if index > 1:
        filename += f"_{index}"
    filename += ".csv"
    return os.path.join(base_path, filename)

def log_scrape_info(timestamp, contest_summary):
    log_entry = f"Scrape Timestamp: {timestamp}, Number of Contest Types: {len(contest_summary)}"
    for contest_type, count in contest_summary.items():
        log_entry += f", {contest_type}: {count} player pools"
    log_entry += "\n"
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_entry)

def fetch_tennis_slate():
    start_time = datetime.now()

    contests = get_contests(tennis_sport_code)
    if not contests:
        return

    draft_groups = {}
    for contest in contests.get('Contests', []):
        draft_group_id = contest.get('dg')
        game_type = contest.get('gameType', 'Unknown')
        if draft_group_id:
            draft_groups[draft_group_id] = game_type
    
    all_player_pools = []
    for draft_group_id in draft_groups.keys():
        player_pool = get_player_pool(draft_group_id)
        if player_pool and 'draftables' in player_pool:
            all_player_pools.append((draft_group_id, player_pool))
    
    # Ensure the output and log directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_counter = {}
    
    # Create a CSV file for each draft group
    for draft_group_id, player_pool in all_player_pools:
        draftables = player_pool.get('draftables', [])
        game_type = draft_groups.get(draft_group_id, 'Unknown')
        
        if not draftables:
            continue
        
        if game_type not in file_counter:
            file_counter[game_type] = 1
        else:
            file_counter[game_type] += 1

        index = 1
        while True:
            file_path = generate_file_path(output_dir, date_str, index)
            if not os.path.exists(file_path):
                break
            index += 1

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Position', 'Salary', 'Contest Type'])
            for player in draftables:
                name = player.get('displayName', 'N/A')
                position = player.get('position', 'N/A')
                salary = player.get('salary', 'N/A')
                writer.writerow([name, position, salary, game_type])

    end_time = datetime.now()
    elapsed_time = end_time - start_time

    # Print elapsed time and contest summary to the terminal
    print(f"Number of Contest Types: {len(file_counter)}", end="")
    for contest_type, count in file_counter.items():
        print(f", {contest_type}: {count} player pools", end="")
    print(f", Elapsed Time: {elapsed_time}")

    # Log the detailed information with timestamp
    log_scrape_info(timestamp, file_counter)

if __name__ == "__main__":
    fetch_tennis_slate()

