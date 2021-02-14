from nba_api.stats.endpoints import (teamplayeronoffdetails,
                                     leaguehustlestatsplayer,
                                     teamplayerdashboard,
                                     playerestimatedmetrics,
                                     fantasywidget)
from nba_api.stats.static import teams, players
import pandas as pd
from pandas import DataFrame
from math import floor
from statistics import median


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

fantasy_pts_by_round = {i: [] for i in range(1, 17)}

def get_fantasy_adp_df():
    # All credit for ADP goes to CBS Sports.
    url = 'https://www.cbssports.com/fantasy/basketball/draft/averages/'
    df = pd.read_html(url)[0]
    fantasy_adp_df = df[['Player', 'Avg Pos']]
    return fantasy_adp_df

def create_fantasy_df():
    adp_df = get_fantasy_adp_df()
    total_fantasy_players = adp_df['Player']
    player_id_df = create_active_players_df()
    fantasy_data_df = fantasywidget.FantasyWidget().get_data_frames()[0]
    dfs_list = []

    for index, row in player_id_df.iterrows():
        player = row['Player']
        pid = row['id']

        # Continue if we don't have ADP data for this player.
        if not adp_df['Player'].str.contains(player).sum():
            continue
        player_df = adp_df[adp_df['Player'].str.contains(player)]
        player_adp = float(player_df['Avg Pos'])

        player_fantasy_data = fantasy_data_df.loc[fantasy_data_df['PLAYER_ID'] == pid].copy()
        fantasy_avgs = (player_fantasy_data['NBA_FANTASY_PTS'])

        if type(fantasy_avgs) == pd.core.series.Series:
            if fantasy_avgs.size > 1:
                fantasy_avgs = fantasy_avgs.mean()
            elif fantasy_avgs.size == 0:
                fantasy_avgs = 0
            else:
                fantasy_avgs = fantasy_avgs.values
        fantasy_avgs = float(fantasy_avgs)
        new_df = DataFrame(data=[[player, player_adp, fantasy_avgs]], columns=['Player', 'ADP', 'Fantasy Average Per Game'])
        round_drafted = 1 if round(player_adp) / 10 <= 1 else floor(round(player_adp) / 10)
        fantasy_pts_by_round[round_drafted].append(fantasy_avgs)
        dfs_list.append(new_df)
    # Create single df containing individual player fantasy data
    combined_fantasy_data_df = pd.concat(dfs_list)
    return combined_fantasy_data_df

def create_active_players_df():
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

def find_round_avg_fantasy_pts():
    median_round_pts = {}
    for round in fantasy_pts_by_round:
        median_val = median(fantasy_pts_by_round[round])
        median_round_pts[round] = median_val
    return median_round_pts