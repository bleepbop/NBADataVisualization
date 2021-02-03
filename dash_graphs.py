import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from data_init import *
import dash_bootstrap_components as dbc

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
                             "Fantasy Average Per Game": "Average Fantasy Points/Game"
                         },)

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
                    persistence=True
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
                        persistence=True
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
                        persistence=True
                        )
            ]
        )
    ],
    body=True
)

# Create the app
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Create the general app layout
app.layout = dbc.Container(
    children=[
        html.H1(children='NBA Data Visualizer', style={'textAlign': 'center'}),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id='nba-scatter-plot', figure=nba_fig), md=8),
            ],
            align="center",
        ),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='fantasy-adp-plot', figure=fantasy_fig))]
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

app.run_server(debug=True, use_reloader=True)