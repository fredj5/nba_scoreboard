from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import cumestatsteamgames, cumestatsteam, gamerotation, leagueleaders
import pandas as pd
import numpy as np
import json
import difflib
import time
import requests


# Retry Wrapper
# Decorator function to prevent HTTP timeouts 
def retry(func, retries=3):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(30)
                attempts += 1

    return retry_wrapper


teams = teams.get_teams()

data = cumestatsteamgames.CumeStatsTeamGames(
    league_id=00,
    season='2022-23',
    season_type_all_star='Regular Season',
    team_id=1610612738,
    outcome_nullable=None
)
