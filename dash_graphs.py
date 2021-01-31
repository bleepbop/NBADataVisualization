import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from data_init import *

NBA_TEAMS = get_teams()
philly = teams.find_teams_by_city('Philadelphia')[0]['id']
combined_data = init_dataframe(philly)
# Create figure
x_value = "E_DEF_RATING"
y_value = "DEFLECTIONS"
nba_fig = px.scatter(combined_data, x=x_value, y=y_value, size='W_PCT', color='PLAYER_NAME')

# Create the app
app = dash.Dash()
app.layout = html.Div(
    children=[
        html.H1(children='NBA Data Visualizer', style={'textAlign': 'center'}),
        dcc.Graph(id='nba-scatter-plot', figure=nba_fig),
        dcc.Dropdown(
            id="dropdown-nba-team",
            options=[{'label': team['full_name'], 'value': team['id']} for team in NBA_TEAMS],
            placeholder="Insert team name",
            persistence=True
        ),
        dcc.Dropdown(
                    id='x-coord-dropdown',
                    options=[{'label': i, 'value': i} for i in combined_data.columns],
                    placeholder='Select a X Coordinate Parameter',
                    persistence=True),
        dcc.Dropdown(
                    id='y-coord-dropdown',
                    options=[{'label': i, 'value': i} for i in combined_data.columns],
                    placeholder='Select a X Coordinate Parameter',
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
    return px.scatter(dataset, x=x_parameter, y=y_parameter, size='W_PCT', color='PLAYER_NAME')

app.run_server(debug=True, use_reloader=True)