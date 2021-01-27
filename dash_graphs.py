import dash
import dash_core_components as dcc
import dash_html_components as html
from data_init import *

combined_data = init_dataframe()
# Create figure
nba_fig = px.scatter(combined_data, x="E_DEF_RATING", y="DEFLECTIONS", size='W_PCT', color='PLAYER_NAME')

# Create the app
app = dash.Dash()
app.layout = html.Div(
    children=[html.H1(children='NBA Data Visualizer', style={'textAlign': 'center'}),
    dcc.Graph(figure=nba_fig),
    dcc.Dropdown(options=[{'label': i, 'value': i} for i in combined_data.columns])
])

app.run_server(debug=True, use_reloader=False)