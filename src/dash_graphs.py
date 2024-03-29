import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from espn_api.basketball import League
import plotly.express as px
import plotly.graph_objects as go

from data_init import *

NBA_TEAMS = get_teams()
# Initial team will be Philly
philly = teams.find_teams_by_city('Philadelphia')[0]['id']
combined_data = init_dataframe(philly)

# Create initial figure w/ default parameters.
x_value = "E_DEF_RATING"
y_value = "DEFLECTIONS"
nba_fig = px.scatter(combined_data, x=x_value, y=y_value, size='W_PCT', color='PLAYER_NAME')
fantasy_df = create_fantasy_df()
fantasy_fig = px.scatter(fantasy_df,
                         x='ADP',
                         y='Fantasy Average Per Game',
                         labels={
                             "Player": "Player Name",
                             "ADP": "Average Draft Position",
                             "Fantasy Average Per Game": "Average Fantasy Points Per Game"
                         },
                         hover_name="Player")
median_fantasy_pts_per_round = find_round_avg_fantasy_pts()
player_clutch_data = player_clutch_data(nba_allstars_2021)
print(player_clutch_data.columns)
clutch_efficiency_fig = px.scatter_ternary(player_clutch_data, a="FG_PCT", b="FT_PCT", c="AST_TO_TOV", hover_name="PLAYER_NAME",
                                           color="PLAYER_NAME", title='NBA Allstars 2021 Clutch Efficiency')
clutch_win_pct_fig = px.scatter_3d(player_clutch_data, x='FG_PCT', y='AST_TO_TOV', z='W_PCT', color='PLAYER_NAME',
                                   hover_name='PLAYER_NAME', title='Offensive Percentages in Relation to Win Percentage')

# Create figure controls.
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Select Team'),
                dcc.Dropdown(
                    id="dropdown-nba-team",
                    options=[{'label': team['full_name'], 'value': team['id']} for team in NBA_TEAMS],
                    placeholder="Insert team name",
                    persistence=True,
                    style={'color': 'black'}
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('X Axis'),
                dcc.Dropdown(
                    id='x-coord-dropdown',
                    options=[{'label': i, 'value': columns_dict[i]} for i in columns_dict],
                    placeholder='Select a X Coordinate Parameter',
                    persistence=True,
                    style={'color': 'black'}
                )
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label('Y Axis'),
                dcc.Dropdown(
                    id='y-coord-dropdown',
                    options=[{'label': i, 'value': impact_stats_dict[i]} for i in impact_stats_dict],
                    placeholder='Select a Y Coordinate Parameter',
                    persistence=True,
                    style={'color': 'black'}
                )
            ]
        )
    ],
    body=True,
    color='primary'
)

search_controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('Highlight Player'),
                dcc.Dropdown(
                    id="input-fantasy-player",
                    options=[{'label': player, 'value': player} for player in fantasy_df['Player']],
                    placeholder="Insert player name",
                    persistence=True,
                    multi=True,
                    style={'color': 'black'}
                ),
            ]
        ),
    ],
    body=True,
    color='primary'
)

fantasy_hub_controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label('ESPN League Input'),
                html.Br(),
                dcc.Input(
                    id="input_league_id",
                    type="number",
                    placeholder="ESPN League ID",
                    persistence=True
                ),
                html.Br(),
                dcc.Input(
                    id="input_league_year",
                    type="number",
                    placeholder="Fantasy League Year",
                    persistence=True
                )
            ]
        ),
    ],
    body=True,
    color='primary'
)

# Create the app
app = dash.Dash(
    external_stylesheets=[dbc.themes.DARKLY]
)

# Create the general app layout
app.layout = dbc.Container(
    children=[
        html.H1(children='NBA Data Visualizer', style={'textAlign': 'center', 'background-color':'primary'}),
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink("Hustle Stats Plot", href="#hustle-stats-plot-header", external_link=True)),
                dbc.NavItem(dbc.NavLink("Fantasy Tools", href="#fantasy-plot-header", external_link=True)),
                dbc.NavItem(dbc.NavLink("ESPN Fantasy League Dashboard", href="#fantasy-hub", external_link=True)),
            ],
            brand='Created by bleebop',
            brand_href='https://github.com/bleepbop?tab=repositories',
            color="primary",
            dark=True,
        ),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H3(children='Clutch Data Visualiztions', style={'textAlign': 'center'}, id='clutch-data-plot-header'),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='clutch-ternary-plot', figure=clutch_efficiency_fig)),
                dbc.Col(dcc.Graph(id='clutch-3d-plot', figure=clutch_win_pct_fig))
            ]
        ),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H3(children='Hustle Stats Plots', style={'textAlign': 'center'}, id='hustle-stats-plot-header'),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id='nba-scatter-plot', figure=nba_fig), md=8),
            ],
            align="start",
        ),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H3(children='Fantasy Value per ADP', style={'textAlign': 'center'}, id='fantasy-plot-header'),
        dbc.Row(
            [
                dbc.Col(search_controls, md=4),
                dbc.Col(dcc.Graph(id='fantasy-adp-plot', figure=fantasy_fig))
            ],
            align="start",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Table(id='selected-players-table'),
                    width={"size": 8, "offset": 4}
                )
            ]
        ),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.Hr(),
        html.H3(children='ESPN Fantasy League Hub', style={'textAlign': 'center'}, id='fantasy-hub'),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(children=[fantasy_hub_controls, dbc.Table(id='standings-table')], md=4),
                dbc.Col(id='fantasy-team-scoring')
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(id='fantasy-league-team-comparison'),
                dbc.Col(id='fantasy-league-category-comparison')
            ],
            align="start"

        )

    ],
    fluid=True,
)

@app.callback(
    Output(component_id='nba-scatter-plot', component_property='figure'),
    Input(component_id='x-coord-dropdown', component_property='value'),
    Input(component_id='y-coord-dropdown', component_property='value'),
    Input(component_id='dropdown-nba-team', component_property='value'),
)
# This callback method takes in control parameters and updates the plot accordingly.
def update_scatter(input_x_value, input_y_value, team_id):
    if input_x_value == None and input_y_value == None and team_id == None:
        input_x_value = "E_DEF_RATING"
        input_y_value = "DEFLECTIONS"
        team_id = philly
    dataset = init_dataframe(team_id)
    return px.scatter(dataset, x=input_x_value, y=input_y_value, size='W_PCT', color='PLAYER_NAME')

@app.callback(
    Output(component_id='fantasy-adp-plot', component_property='figure'),
    Input(component_id='input-fantasy-player', component_property='value')
)
def update_traces(data):
    fantasy_fig = px.scatter(fantasy_df,
                             x='ADP',
                             y='Fantasy Average Per Game',
                             labels={
                                 "Player": "Player Name",
                                 "ADP": "Average Draft Position",
                                 "Fantasy Average Per Game": "Average Fantasy Points Per Game"
                             },
                             hover_name="Player")
    if data == None or len(data) == 0:
        return fantasy_fig
    player_data = []
    for player in data:
        player_data.append(fantasy_df.loc[fantasy_df['Player'] == player].copy())
    trace_data = pd.concat(player_data)
    fantasy_fig.add_scatter(x=trace_data['ADP'],
                            y=trace_data['Fantasy Average Per Game'],
                            mode="markers",
                            text=['<b>{}</b><br><br>ADP: {}<br>Avg Fantasy PPG: {}'.format(str(row["Player"]),
                                                                                           str(row["ADP"]),
                                                                                           str(row['Fantasy Average Per Game'])) for index, row in trace_data.iterrows()],
                            cliponaxis=True,
                            name='Selected Players',
                            meta='')
    return fantasy_fig

@app.callback(
    Output(component_id='selected-players-table', component_property='children'),
    Input(component_id='input-fantasy-player', component_property='value')
)
def update_table(data):
    if data == None or len(data) == 0:
        return
    player_data = []
    for player in data:
        df = fantasy_df.loc[fantasy_df['Player'] == player].copy()
        avg_round = 1 if round(df['ADP'].values[0]) / 10 <= 1 else round(df['ADP'].values[0] / 10)
        round_median = median_fantasy_pts_per_round[avg_round]
        df['Draft Round Median Fantasy PPG'] = round_median
        player_data.append(df)
    trace_data = pd.concat(player_data)
    table = dbc.Table.from_dataframe(trace_data, striped=True, bordered=True, hover=True)
    return table

@app.callback(
    Output(component_id='standings-table', component_property='children'),
    Input(component_id='input_league_id', component_property='value'),
    Input(component_id='input_league_year', component_property='value'),
)
def init_fantasy_league(league_id, league_year):
    if league_id == None or league_year == None:
        return
    league = League(league_id, league_year)

    # Create standings table
    body = [html.Thead(html.Tr([html.Th("League Standings")]))]
    standings_index = 1
    for team in league.standings():
        row = html.Tr([html.Td(standings_index), html.Td(team.team_name)])
        standings_index += 1
        body.append(row)
    table = dbc.Table(body)
    return table

@app.callback(
    Output(component_id='fantasy-team-scoring', component_property='children'),
    Output(component_id='fantasy-league-team-comparison', component_property='children'),
    Output(component_id='fantasy-league-category-comparison', component_property='children'),
    Input(component_id='input_league_id', component_property='value'),
    Input(component_id='input_league_year', component_property='value'),
)
def init_fantasy_team_scoring(league_id, league_year):
    if league_id == None or league_year == None:
        return
    league = League(league_id, league_year)
    teams = {team.team_id: team for team in league.teams}
    team_scoring = {}

    weekly_scoring_figure = go.Figure(layout_title_text='Fantasy Team Weekly Performance')
    team_data = []
    category_data = []

    for team in league.standings():
        team_id = team.team_id
        team_scoring[team.team_name] = {'scoring': [], 'wins': []}
        weekly_metrics = {'Week': [], 'Score': []}
        team_categories = {'PTS': 0, 'BLK': 0, 'STL': 0, 'AST': 0, 'REB': 0, 'TO': 0, 'FGM': 0, 'FGA': 0, 'FTM': 0, 'FTA': 0, '3PTM': 0}
        week_idx = 1
        points_for = 0
        points_against = 0
        for matchup in team.schedule:
            home_status = True if matchup.home_team.team_id == team_id else False
            weekly_score = 0
            if home_status:
                weekly_score = matchup.home_final_score
                points_for += matchup.home_final_score
                points_against += matchup.away_final_score
                if matchup.home_team_cats is not None:
                    for cat in matchup.home_team_cats:
                        if len(cat) == 0 or cat is None:
                            continue
                        team_categories[cat] += matchup.home_team_cats[cat]['score']
            else:
                weekly_score = matchup.away_final_score
                points_for += matchup.away_final_score
                points_against += matchup.home_final_score
                if matchup.away_team_cats is not None:
                    for cat in matchup.away_team_cats:
                        if len(cat) == 0 or cat is None:
                            continue
                        team_categories[cat] += matchup.away_team_cats[cat]['score']
            team_scoring[team.team_name]['scoring'].append(weekly_score)
            win_status = True if matchup.winner == team.team_name else False
            team_scoring[team.team_name]['wins'].append(win_status)
            weekly_metrics['Week'].append(week_idx)
            weekly_metrics['Score'].append(weekly_score)
            week_idx += 1
        # Update Categories data
        team_categories['FT%'] = team_categories['FTM'] / team_categories['FTA']
        del team_categories['FTM']
        del team_categories['FTA']
        team_categories['FG%'] = team_categories['FGM'] / team_categories['FGA']
        del team_categories['FGM']
        del team_categories['FGA']
        for cat in team_categories:
            # Tuple is of form: Team Name - Category Name - Category Value
            category_data.append((team.team_name, cat, team_categories[cat]))
        weekly_scoring_figure.add_trace(go.Scatter(x=weekly_metrics['Week'],
                                                   y=weekly_metrics['Score'],
                                                   name=team.team_name))
        team_data.append([team.team_name, points_for, points_against])
    # scoring_df = pd.DataFrame.from_dict(team_scoring)
    team_comparison_df = pd.DataFrame(team_data, columns=['Team Name', 'Points For', 'Points Against'])
    team_comparison_plot = px.scatter(team_comparison_df,
                                      x='Points Against',
                                      y='Points For',
                                      hover_name="Team Name",
                                      size='Points For',
                                      color='Team Name',
                                      title='Fantasy Team Comparison')
    category_df = pd.DataFrame(category_data, columns=['Team', 'Category', 'Count'])
    team_category_bargraph = px.bar(category_df, x="Team", y='Count', color="Category", title="Fantasy Team Category Performance")

    return dcc.Graph(figure=weekly_scoring_figure), dcc.Graph(figure=team_comparison_plot), dcc.Graph(figure=team_category_bargraph)

app.run_server(host='0.0.0.0', port=8000, debug=True)