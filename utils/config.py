# sports_sim/utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

PROCESSED_DATA_DIR = os.getenv('PROCESSED_DATA_DIR', 'data/processed/')
FULL_MERGED_FILE = os.getenv('FULL_MERGED_FILE', 'data/processed/full_merged.csv')
SLIMMED_PROJECTIONS_FILE = os.getenv('SLIMMED_PROJECTIONS_FILE', 'data/processed/slimmed_projections.csv')
