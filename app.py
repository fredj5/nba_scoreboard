from flask import Flask, jsonify
from nba_api.stats.static import teams
from nba_api.stats.endpoints import cumestatsteamgames, leagueleaders, scoreboardv2
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import requests
import difflib
import time
import os

app = Flask(__name__)

def retry(func, retries=3):
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(f"Retrying due to: {e}")
                time.sleep(10)
                attempts += 1
        raise Exception("API failed after retries.")
    return wrapper

nba_teams = teams.get_teams()

def find_team_id(team_name):
    names = [team["full_name"] for team in nba_teams]
    match = difflib.get_close_matches(team_name, names, n=1)
    if match:
        return next(team["id"] for team in nba_teams if team["full_name"] == match[0])
    return None

@retry
def get_team_game_stats(team_id):
    stats = cumestatsteamgames.CumeStatsTeamGames(
        league_id='00',
        season='2024-25',
        season_type_all_star='Playoffs',
        team_id=team_id
    )
    return stats.cume_stats_team_games.get_data_frame()

@retry
def get_top_scorers():
    leaders = leagueleaders.LeagueLeaders(
        stat_category_abbreviation='PTS',
        season='2024-25',
        season_type_all_star='Playoffs',
    )
    df = leaders.league_leaders.get_data_frame()
    return df[['PLAYER', 'TEAM', 'PTS']].head(10)

@retry
def get_playoff_games():
    from datetime import datetime
    today = datetime.now().strftime('%m/%d/%Y')
    
    scoreboard = scoreboardv2.ScoreboardV2(
        game_date=today,
        league_id='00',
    )
    
    data_frames = scoreboard.get_data_frames()
    
    print(f"DEBUG: Number of data frames: {len(data_frames)}")
    for i, df in enumerate(data_frames):
        print(f"DEBUG: DataFrame {i} columns: {df.columns.tolist()}")
        print(f"DEBUG: DataFrame {i} sample data:\n{df.head()}")
    
    # Return empty list so the API still works without error
    return []




@app.route('/')
def index():
    return jsonify({"message": "NBA Scoreboard API is running!"})

@app.route('/leaders')
def leaders():
    df = get_top_scorers()
    return jsonify(df.to_dict(orient='records'))

@app.route('/team_stats/<team_name>')
def team_stats(team_name):
    team_id = find_team_id(team_name)
    if team_id is None:
        return jsonify({"error": "Team not found"}), 404
    df = get_team_game_stats(team_id)
    return jsonify(df.to_dict(orient='records'))

@app.route('/games')
def games():
    try:
        games = get_playoff_games()
        if not games:
            return jsonify({"message": "No games currently in progress or completed today."})
        return jsonify(games)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@retry
def get_player_career_stats(player_id):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]  # usually first df is season-by-season stats
    return df

def find_player_id(player_name):
    all_players = players.get_players()
    names = [p['full_name'] for p in all_players]
    match = difflib.get_close_matches(player_name, names, n=1)
    if match:
        return next(p['id'] for p in all_players if p['full_name'] == match[0])
    return None
    
@app.route('/player_career_stats/<player_name>')
def player_career_stats(player_name):
    player_id = find_player_id(player_name)
    if player_id is None:
        return jsonify({"error": "Player not found"}), 404
    df = get_player_career_stats(player_id)
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
