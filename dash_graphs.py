import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from data_init import *

NBA_TEAMS = get_teams()
# Initial team will be Philly
philly = teams.find_teams_by_city('Philadelphia')[0]['id']
combined_data = init_dataframe(philly)

# Create figure w/ default parameters.
x_value = "E_DEF_RATING"
y_value = "DEFLECTIONS"
nba_fig = px.scatter(combined_data, x=x_value, y=y_value, size='W_PCT', color='PLAYER_NAME')

# Create the app
app = dash.Dash()
app.layout = html.Div(
    children=[
        html.H1(children='NBA Data Visualizer', style={'textAlign': 'center'}),
        dcc.Graph(id='nba-scatter-plot', figure=nba_fig),
        html.Label(
            htmlFor='dropdown-nba-team',
            children=['Select team: ']
        ),
        dcc.Dropdown(
            id="dropdown-nba-team",
            options=[{'label': team['full_name'], 'value': team['id']} for team in NBA_TEAMS],
            placeholder="Insert team name",
            persistence=True
        ),
        html.Label(
            htmlFor='x-coord-dropdown',
            children=['Select X Parameter: ']
        ),
        dcc.Dropdown(
                    id='x-coord-dropdown',
                    options=[{'label': i, 'value': columns_dict[i]} for i in columns_dict],
                    placeholder='Select a X Coordinate Parameter',
                    persistence=True),
        html.Label(
            htmlFor='y-coord-dropdown',
            children=['Select Y Parameter: ']
        ),
        dcc.Dropdown(
                    id='y-coord-dropdown',
                    options=[{'label': i, 'value': impact_stats_dict[i]} for i in impact_stats_dict],
                    placeholder='Select a Y Coordinate Parameter',
                    persistence=True)
    ]
)

@app.callback(
    Output(component_id='nba-scatter-plot', component_property='figure'),
    Input(component_id='x-coord-dropdown', component_property='value'),
    Input(component_id='y-coord-dropdown', component_property='value'),
    Input(component_id='dropdown-nba-team', component_property='value'),
)
def update_scatter(input_x_value, input_y_value, team_id):
    dataset = init_dataframe(team_id)
    print(dataset.columns)
    return px.scatter(dataset, x=input_x_value, y=input_y_value, size='W_PCT', color='PLAYER_NAME')

app.run_server(debug=True, use_reloader=True)