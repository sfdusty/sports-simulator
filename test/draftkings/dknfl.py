import requests
import datetime
import csv
import os
import logging
import random
import time

# List of user-agent strings
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
]

API_KEY = 'AIzaSyDJ1BoKe8OR3X0itmt7QIJToMe-wh5mEX8'
save_directory = '/home/ds/Desktop/inprogress/dk'

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_contests(sport_code):
    url = f"https://www.draftkings.com/lobby/getcontests?sport={sport_code}"
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch contests for sport code {sport_code}: {e}")
        return None

def get_player_pool(draft_group_id):
    url = f"https://api.draftkings.com/draftgroups/v1/draftgroups/{draft_group_id}/draftables?apiKey={API_KEY}"
    headers = {'User-Agent': get_random_user_agent()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch player pool for Draft Group ID {draft_group_id}: {e}")
        return None

def parse_iso_time(timestamp):
    try:
        return datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return datetime.datetime.strptime(timestamp[:26], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')

def save_to_csv(filename, player_data):
    if not player_data:
        logging.warning("No player data to save.")
        return

    keys = player_data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(player_data)

def main():
    sport_code = 'NFL'
    logging.basicConfig(filename=f'logs/{sport_code.lower()}_classic_scraper.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
    logging.info(f"Fetching contests for sport code: {sport_code} and game type: Classic")
    
    contests = get_contests(sport_code)
    if not contests:
        logging.error("Failed to retrieve contests.")
        return

    draft_group_ids = set()
    for contest in contests.get('Contests', []):
        game_type = contest.get('gameType')
        if game_type == "Classic":
            draft_group_id = contest.get('dg')
            if draft_group_id:
                draft_group_ids.add(draft_group_id)
                break

    if not draft_group_ids:
        logging.warning("No relevant Draft Group IDs found for Classic.")
        return

    draft_group_id = list(draft_group_ids)[0]
    logging.info(f"Fetching player pool for Draft Group ID: {draft_group_id}")
    player_pool = get_player_pool(draft_group_id)

    if player_pool and 'draftables' in player_pool:
        draftables = player_pool['draftables']
        player_data = []
        for player in draftables:
            player_info = {
                "Player ID": player['playerId'],
                "Name": player['displayName'],
                "Position": player['position'],
                "Salary": player['salary'],
                "Team": player.get('teamAbbreviation', 'N/A'),
                "Competition": player.get('competition', {}).get('name', 'N/A'),
                "Start Time": parse_iso_time(player.get('competition', {}).get('startTime', '1970-01-01T00:00:00Z'))
            }
            player_data.append(player_info)
        
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            logging.info(f"Created directory: {save_directory}")

        csv_file_path = os.path.join(save_directory, f'{sport_code.lower()}_classic_player_pool.csv')
        save_to_csv(csv_file_path, player_data)
        logging.info(f"Player pool data saved to {csv_file_path}")

        if os.path.exists(csv_file_path):
            logging.info(f"File successfully saved: {os.path.abspath(csv_file_path)}")
        else:
            logging.error("File save failed.")
    else:
        logging.warning("No player pool found for the selected Draft Group ID.")

if __name__ == "__main__":
    main()

