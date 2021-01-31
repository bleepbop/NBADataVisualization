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
    html.Div(children=[
        html.Table(children=[
            html.Colgroup(children=[
                html.Col(),
                html.Col(),
                html.Col()
            ]),
            html.Tr(children=[
                html.Td(children=[html.B('X Coordinate Parameter')]),
                html.Td(),
                html.Td(children=[html.B('Y Coordinate Parameter')]),
            ]),
            html.Colgroup(children=[
                html.Col(),
                html.Col(),
                html.Col() # Figure out persistence properties
            ]),
            html.Tr(children=[
                html.Td(children=[
                    dcc.Dropdown(
                        id='x-coord-dropdown',
                        options=[{'label': i, 'value': i} for i in combined_data.columns],
                        placeholder='Select a X Coordinate Parameter',
                        persistence=True)
                ]),
                html.Td(),
                html.Td(children=[
                    dcc.Dropdown(
                        id='y-coord-dropdown',
                        options=[{'label': i, 'value': i} for i in combined_data.columns],
                        placeholder='Select a X Coordinate Parameter',
                        persistence=True)
                ])
            ])
        ])
    ])
])

app.run_server(debug=True, use_reloader=False)