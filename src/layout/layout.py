from dash import dcc, html
import dash_bootstrap_components as dbc

def update_layout(app, dashboard):
    app.layout = dbc.Container(
        [
            html.H1("Temperature Data Analysis App"),
            html.Hr(),
            dbc.Row(html.H1("Control Dashboard")),
            dbc.Row(
                [
                    dbc.Col(dashboard, md=4),
                    dbc.Col(dcc.Graph(id="temperature_graph"), md=8),
                ],
                align="center",
            ),
        ],
        fluid=True,
    )
