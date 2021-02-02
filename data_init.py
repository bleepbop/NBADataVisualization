from nba_api.stats.endpoints import (commonplayerinfo,
                                     teamplayeronoffdetails,
                                     leaguehustlestatsplayerleaders,
                                     leaguehustlestatsplayer,
                                     teamplayerdashboard,
                                     teaminfocommon,
                                     playerestimatedmetrics,
                                     playerfantasyprofile)
from nba_api.stats.static import teams, players
from pandas import DataFrame
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re

columns_dict = {"Contested Shots": "CONTESTED_SHOTS",
                "Contested 2 Pt Shots": "CONTESTED_SHOTS_2PT",
                "Contested 3 Pt Shots": "CONTESTED_SHOTS_3PT",
                "Deflections": "DEFLECTIONS",
                "Charges Drawn": "CHARGES_DRAWN",
                "Screen Assists": "SCREEN_ASSISTS",
                "Screen Assist Pts": "SCREEN_AST_PTS",
                "Offensive Loose Balls Recovered": "OFF_LOOSE_BALLS_RECOVERED",
                "Defensive Loose Balls Recovered": "DEF_LOOSE_BALLS_RECOVERED",
                "Loose Balls Recovered": "LOOSE_BALLS_RECOVERED",
                "Offensive Boxouts": "OFF_BOXOUTS",
                "Defensive Boxouts": "DEF_BOXOUTS"
                }

impact_stats_dict = {"Offensive Rating": 'E_OFF_RATING',
                     "Defensive Rating": 'E_DEF_RATING',
                     "Net Rating": 'E_NET_RATING',
                     "Win Percent": 'W_PCT'}

def get_fantasy_adp_df():
    url = 'https://www.cbssports.com/fantasy/basketball/draft/averages/'
    df = pd.read_html(url)[0]
    fantasy_adp_df = df[['Player', 'Avg Pos']]
    return fantasy_adp_df

def create_fantasy_df():
    adp_df = get_fantasy_adp_df()
    total_players = adp_df['Player']
    dfs_list = []
    for player in total_players:
        regex = re.compile(r'^{}$'.format(player))
        player = players.find_players_by_full_name(regex)['PLAYER_ID']
        fantasy_df = playerfantasyprofile.PlayerFantasyProfile().get_data_frames()[4]  # Return the 'Overall' df
        fantasy_df['Player'] = player
        dfs_list.append(fantasy_df[['Player', 'NBA_FANTASY_PTS']])
    # Create single df containing individual player fantasy data
    combined_fantasy_data_df = pd.concat(df_list)
    # Merge on player name
    merged_df = pd.merge(adp_df, combined_fantasy_data_df, on='Player')
    return

def create_players_df():
    all_players = players.get_active_players()
    df = pd.DataFrame(all_players)
    df.rename(columns = {'full_name':'Player'}, inplace = True)
    pid_df = df[['id', 'Player']]
    return pid_df

def get_teams():
    team_info = teams.get_teams()
    return team_info

def init_dataframe(team_id):
    metrics = playerestimatedmetrics.PlayerEstimatedMetrics().get_data_frames()[0]

    '''
    info = teamplayeronoffdetails.TeamPlayerOnOffDetails(team_id=philly['id'])
    players_on = info.get_data_frames()[1]
    players_off = info.get_data_frames()[2]
    '''

    # Get player names for a given team
    team = teamplayerdashboard.TeamPlayerDashboard(team_id=team_id)
    team_df = team.get_data_frames()[1]
    roster = team_df[['PLAYER_ID', 'PLAYER_NAME']]

    hustle_stats = leaguehustlestatsplayer.LeagueHustleStatsPlayer()
    hustle_df = hustle_stats.get_data_frames()[0]

    # Remove unnecessary columns
    del hustle_df['PCT_BOX_OUTS_OFF']
    del hustle_df['PCT_BOX_OUTS_DEF']

    # Columns to normalize:
    cols = columns_dict.values()

    team_metrics = []
    df_list = []
    for player_id in roster['PLAYER_ID']:
        player_df = hustle_df.loc[hustle_df['PLAYER_ID'] == player_id].copy()
        games_played = player_df['G']
        # Normalize Data to per game stats.
        for col in cols:
            player_df[col] = player_df[col] / games_played
        df_list.append(player_df)
        player_metrics_df = metrics.loc[metrics['PLAYER_ID'] == player_id]
        team_metrics.append(player_metrics_df[["PLAYER_ID", "E_OFF_RATING", "E_DEF_RATING", "E_NET_RATING", "W_PCT"]])

    team_hustle_df = pd.concat(df_list)
    player_metrics_df = pd.concat(team_metrics)
    # Merge dataframes on player name.
    merged_df = pd.merge(team_hustle_df, player_metrics_df, on='PLAYER_ID')
    return merged_df