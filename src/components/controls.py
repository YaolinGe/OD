from dash import html, dcc
import dash_bootstrap_components as dbc


def get_dashboard(temperature_cases):
    dashboard = dbc.Card([
        html.Div([
            dbc.Label("Select a temperature ℃"),
            dcc.Dropdown(id="temperature_case",
                            options=[{"label": "{:d} ℃".format(case), "value": case} for case in temperature_cases],
                            value=temperature_cases[0]),
        ]),
        html.Div([
            dbc.Label("Select a sensor "),
            dcc.RadioItems(options=['Sensor I', 'Sensor II'], value="Sensor II", id="sensor"),
        ]),
        html.Div([
            dbc.Label("Select a time window"),
            dcc.Slider(id="slider_timewindow", min=0, max=100, step=10, value=0),
        ]),
        html.Div([
            dbc.Label("Time slider"),
            dcc.Slider(id="slider", min=0, max=100, marks=None, value=0),
        ]),
    ], body=True)
    return dashboard
