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
            dbc.Label("Select a smoothing algorithm"),
            dcc.RadioItems(id="smoother", options=['Moving average',
                                                   'Gaussian smoothing',
                                                   'Lowess',
                                                   'Savitzky-Golay Filter',
                                                   'Median filter',
                                                   'Kalman filter',
                                                   'Wavelet transform',
                                                   'Fourier transform',
                                                   'Holt-Winters Exponential Smoothing'],
                           value='Moving average'),
        ], style={"align-items": "center"}),
        html.Div([
            dbc.Label("Select a predicting algorithm"),
            dcc.RadioItems(id="predictor", options=['ARIMA',
                                                    # 'SARIMA',
                                                    # 'Gaussian Process',
                                                    ],
                           value='ARIMA')
        ]),
        html.Div([
            dbc.Label("Specify the predicting parameter"),
            dbc.Row([
                dbc.Col([
                    dbc.Col([
                        dbc.Label("p"),
                        dcc.Input(id="p", type="number", value=1),
                    ]),
                    dbc.Col([
                        dbc.Label("d"),
                        dcc.Input(id="d", type="number", value=1),
                    ]),
                    dbc.Col([
                        dbc.Label("q"),
                        dcc.Input(id="q", type="number", value=1),
                    ]),
                ]),
            ])
        ])
    ], body=True)
    return dashboard


def get_timeslider():
    timeslider = dbc.Row([
        dbc.Label("Time slider"),
        dcc.Slider(id="slider", min=2, max=100, marks=None, value=10),
    ])
    return timeslider
