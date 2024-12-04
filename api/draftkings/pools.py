import requests
import pandas as pd
import os
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Constants
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
SAVE_TO_CSV = True  # Set to False to print data to terminal instead of saving to CSV

# Endpoint URLs
SPORTS_ENDPOINT = "https://api.draftkings.com/sites/US-DK/sports/v1/sports?format=json"
CONTESTS_ENDPOINT = "https://www.draftkings.com/lobby/getcontests?sport={sport}"
DRAFTABLES_ENDPOINT = "https://api.draftkings.com/draftgroups/v1/draftgroups/{draftgroup_id}/draftables"

# Session setup with retry mechanism
def get_session():
    """Create a session with retry mechanism for handling transient errors."""
    session = requests.Session()
    retries = Retry(
        total=5,  # Total number of retries
        backoff_factor=0.3,  # Wait time between retries
        status_forcelist=[500, 502, 503, 504],  # Retry on these HTTP statuses
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

# Use session to make requests
session = get_session()

# Debugging
def debug_log(message):
    if DEBUG_MODE:
        print(message)

def fetch_sports():
    """Fetch all sports with their regionAbbreviatedSportName."""
    try:
        response = session.get(SPORTS_ENDPOINT, timeout=5)
        response.raise_for_status()
        sports_data = response.json()
        return [sport['regionAbbreviatedSportName'] for sport in sports_data.get('sports', [])]
    except requests.RequestException as e:
        print(f"Error fetching sports: {e}")
        return []

def fetch_draftables(draftgroup_id):
    """Fetch draftable players for a specific draft group, including playerId, and only returning players with a salary."""
    url = DRAFTABLES_ENDPOINT.format(draftgroup_id=draftgroup_id)
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Only return players with a salary, including playerId
        players = [
            {
                'playerId': player.get('playerId'),
                'displayName': player.get('displayName'),
                'salary': player.get('salary'),
                'teamAbbreviation': player.get('teamAbbreviation')
            }
            for player in data.get('draftables', [])
            if 'salary' in player and player['salary'] is not None
        ]
        debug_log(f"Fetched {len(players)} players with salary for DraftGroupId {draftgroup_id}.")
        return players
    except requests.RequestException as e:
        print(f"Error fetching draftables for DraftGroupId {draftgroup_id}: {e}")
        return []


def fetch_draftgroups(sport):
    """Fetch draft groups for a specific sport, filtering for featured groups where draftables have a salary."""
    url = CONTESTS_ENDPOINT.format(sport=sport)
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Filter to include only draft groups where at least one draftable has a salary
        draftgroups = []
        for group in data.get('DraftGroups', []):
            if group.get("DraftGroupTag") == "Featured":
                draftgroup_id = group['DraftGroupId']
                contest_type_id = group['ContestTypeId']
                game_count = group.get('GameCount', '')
                start_time_suffix = group.get('ContestStartTimeSuffix', '')
                
                # Fetch draftables for this draftgroup_id and check for salary
                players = fetch_draftables(draftgroup_id)
                if players:  # Only add if there's at least one player with a salary
                    draftgroups.append({
                        'DraftGroupId': draftgroup_id,
                        'ContestTypeId': contest_type_id,
                        'GameCount': game_count,
                        'ContestStartTimeSuffix': start_time_suffix,
                        'Players': players
                    })
                    debug_log(f"DraftGroupId {draftgroup_id} added (contains salaried players).")
                else:
                    debug_log(f"DraftGroupId {draftgroup_id} skipped (no salaried players).")
        
        debug_log(f"Found {len(draftgroups)} featured draft groups with salaried players for {sport}.")
        return draftgroups
    except requests.RequestException as e:
        print(f"Error fetching draft groups for {sport}: {e}")
        return []

def save_or_print_data(sport, draftgroup_info):
    """Save each draft group's data to a CSV file or print it based on SAVE_TO_CSV setting."""
    draftgroup_id = draftgroup_info['DraftGroupId']
    contest_type_id = draftgroup_info['ContestTypeId']
    game_count = draftgroup_info['GameCount']
    start_time_suffix = draftgroup_info['ContestStartTimeSuffix']
    players = draftgroup_info['Players']
    
    # Determine filename based on ContestTypeId
    if contest_type_id == 96:
        file_name = f"SD - {start_time_suffix}.csv"
    elif contest_type_id == 21:
        file_name = f"Classic - {game_count} games {start_time_suffix}.csv"
    else:
        file_name = f"{sport}_{draftgroup_id}.csv"  # Default naming if no specific rule
    
    if SAVE_TO_CSV:
        # Create sport-specific directory if it does not exist
        directory = os.path.join(os.getcwd(), sport)
        if not os.path.exists(directory):
            os.makedirs(directory)
            debug_log(f"Created directory: {directory}")
        
        # Convert to DataFrame and save as CSV in the sport-specific directory
        df = pd.DataFrame(players)
        file_path = os.path.join(directory, file_name)
        df.to_csv(file_path, index=False)
        debug_log(f"Data for DraftGroupId {draftgroup_id} saved to {file_path}.")
        return file_path
    else:
        # Print data to terminal instead of saving
        print(f"\nData for {sport} - DraftGroupId {draftgroup_id} - ContestTypeId {contest_type_id}")
        df = pd.DataFrame(players)
        print(df.to_string(index=False))
        return None

def main():
    # Step 1: Fetch sports
    sports = fetch_sports()
    if not sports:
        print("No sports data available.")
        sys.exit(1)

    # Step 2: Loop through each sport and fetch featured draft groups
    for sport in sports:
        debug_log(f"Processing sport: {sport}")
        draftgroup_info_list = fetch_draftgroups(sport)
        
        # Step 3: Track filenames for logging
        saved_files = []
        for draftgroup_info in draftgroup_info_list:
            file_path = save_or_print_data(sport, draftgroup_info)
            if file_path:
                saved_files.append(file_path)

        # Step 4: Summary log for each sport
        if saved_files:
            print(f"\n{len(saved_files)} {sport} slates added: {saved_files}")
        else:
            print(f"\nNo {sport} slates were added.")

if __name__ == "__main__":
    main()

