import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

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
                dbc.Label('X Variable'),
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
                dbc.Label('Y Variable'),
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

# Create the app
app = dash.Dash(
    external_stylesheets=[dbc.themes.DARKLY]
)

# Create the general app layout
app.layout = dbc.Container(
    children=[
        html.H1(children='NBA Data Visualizer', style={'textAlign': 'center', 'background-color':'primary'}),
        html.Hr(),
        html.H3(children='Hustle Stats Plots', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id='nba-scatter-plot', figure=nba_fig), md=8),
            ],
            align="center",
        ),
        html.Hr(),
        html.H3(children='Fantasy Value per ADP', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(search_controls, md=4),
                dbc.Col(dcc.Graph(id='fantasy-adp-plot', figure=fantasy_fig))
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Table(id='selected-players-table'),
                )
            ]
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
    if len(data) == 0:
        return fantasy_fig
    player_data = []
    for player in data:
        player_data.append(fantasy_df.loc[fantasy_df['Player'] == player].copy())
    trace_data = pd.concat(player_data)
    fantasy_fig.add_scatter(x=trace_data['ADP'], y=trace_data['Fantasy Average Per Game'], mode="markers", text=[{'Player': row["Player"], 'ADP': row["ADP"], 'Avg Fantasy PPG': row['Fantasy Average Per Game']} for index, row in trace_data.iterrows()], cliponaxis=True)
    return fantasy_fig

@app.callback(
    Output(component_id='selected-players-table', component_property='children'),
    Input(component_id='input-fantasy-player', component_property='value')
)
def update_table(data):
    if len(data) == 0:
        return
    player_data = []
    for player in data:
        player_data.append(fantasy_df.loc[fantasy_df['Player'] == player].copy())
    trace_data = pd.concat(player_data)
    table = dbc.Table.from_dataframe(trace_data, striped=True, bordered=True, hover=True)
    return table

app.run_server(debug=True, use_reloader=True)