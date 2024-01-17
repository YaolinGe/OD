from dash import html, dcc
import dash_bootstrap_components as dbc


def get_dashboard(temperature_cases):
    """
    Create the dashboard to select the temperature, sensor and time window.
    """
    dashboard = dbc.Card([
        html.Div([
            dbc.Label("Select a temperature ℃"),
            dcc.Dropdown(id="temperature_case",
                         options=[{"label": "{:d} ℃".format(case), "value": case} for case in temperature_cases],
                         value=temperature_cases[-1], multi=False),
        ]),
        html.Div([
            dbc.Label("Select a sensor "),
            dcc.RadioItems(options=['Sensor I', 'Sensor II'], value="Sensor II", id="sensor"),
        ]),
        html.Div([
            dbc.Label("Select a time window"),
            dcc.Input(id="slider_timewindow", type="number", value=10),
        ]),
        html.Div([
            dbc.Label("Smoother"),
            dcc.Dropdown(id="smoother", options=[{"label": "None", "value": "None"}, {"label": "Savitzky-Golay", "value": "Savitzky-Golay"}], value="None", multi=False),
        ])
    ], body=True)
    return dashboard


def get_timeslider():
    timeslider = dbc.Row([
        dbc.Label("Time slider"),
        dcc.Slider(id="slider", min=0, max=100, marks=None, value=0),
    ])
    return timeslider
