from turtle import home
from requests import get
from pprint import PrettyPrinter
from datetime import date
import pandas as pd


BASE_URL = "https://data.nba.net"
ALL_URL = "/prod/v1/today.json"
NBA_PLAYOFF_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
SCHEDULE_URL = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json"

printer = PrettyPrinter()

def get_links(): # DATA.NBA.NET
    data = get(BASE_URL + ALL_URL).json()
    links = data['links']
    return links


def get_game_info(): # SCRAPED FROM NBA SITE
    game_info = get(NBA_PLAYOFF_URL).json()['scoreboard']
    return game_info


def get_finals_schedule(): # LEAGUE SCHEDULE URL
    schedule_info = get(SCHEDULE_URL).json()['leagueSchedule']['gameDates']
    print('NBA FINALS')
    print()
    for i in range(222, 229):
        finals_schedule = schedule_info[i]['games']
        for game in finals_schedule:
            
            arenaName = game['arenaName'] #GENERAL SERIES INFO
            seriesScore = game['seriesText']
            gameNumber = game['seriesGameNumber']

            
            awayTeam = game['awayTeam']['teamName'] # AWAY TEAM INFO
            awayAbrev = game['awayTeam']['teamTricode']
            awayTeamScore = game['awayTeam']['score']
            
            homeTeam = game['homeTeam']['teamName'] # HOME TEAM INFO
            homeAbrev = game['homeTeam']['teamTricode']
            homeTeamScore = game['homeTeam']['score']

            print(awayTeam + " vs. " + homeTeam) #MATCHUP
            print(gameNumber + ' ' + '(' + seriesScore + ')')
            
            print('----------------------------')
            
            print(" " + awayAbrev + "  " + str(awayTeamScore)) #SCORES
            print(" " + homeAbrev + "  " + str(homeTeamScore))
            
            print() # BUFFER
            print()
            # printer.pprint(game)

def get_scoreboard(): # FORMATTING AND PRINTING TO STANDARD OUTPUT
    scoreboard = get_links()['currentScoreboard']
    games = get(BASE_URL + scoreboard).json()['games']

    # DATE
    today = date.today()
    current_date = today.strftime("%B %d, %Y")
    comparison_date = today.strftime('%Y%m%d')
    
    # PRINT DATE
    print()
    print(current_date)
    
    # TIP-OFF, GAME NUMBER, AND SERIES SCORE
    tipoff = get_game_info()['games']
    for data in tipoff:
        tipoff_time = data['gameStatusText']
        series_game_number = data['seriesGameNumber']
        series_score = data['seriesText']
    
    # TEAMS AND CLOCK
    for game in games:
        home_team = game['hTeam']
        away_team = game['vTeam']
        clock = game['clock']
        period = game['period']

        
        # BUFFER
        print('------------') 
        
        # PRINT STATEMENTS
        print(series_game_number + ':' + ' ' + series_score) # GAME NUMBER AND SERIES SCORE
        
        if clock == '' and period['current'] == 4: #
            clock = 'FINAL'
            print(clock)

        if clock == '' and period['current'] == 0:
            clock = 'Tip-off: ' + tipoff_time
            print(clock)

        else:
            print(clock + ' -- Q'+ str(period['current']))

        print()
        print(f"{away_team['triCode']} -- {away_team['score']}") # AWAY TEAM SCORE
        print(f"{home_team['triCode']} -- {home_team['score']}") # HOME TEAM SCORE
        print()
    


# printer.pprint(get_game_info())
# get_scoreboard()
# printer.pprint(get_links())
get_finals_schedule()
