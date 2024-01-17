from dash import dcc, html
import dash_bootstrap_components as dbc


def update_layout(app, dashboard, timeslider):
    app.layout = dbc.Container(
        [
            dbc.Row(html.H1("Control Dashboard"), className="h-5"),
            dbc.Row(
                [
                    dbc.Col(dashboard, width=4, align="start"),
                    dbc.Col([
                        dbc.Row([
                            dbc.Row([dbc.Col(timeslider, width=10)], justify="center", className="h-25"),
                            dbc.Row(dcc.Graph(id="temperature_graph"), align="start", className="h-75"),
                        ])], md=8),
                ],
            ),
        ],
        style={"height": "100vh"},
    )
