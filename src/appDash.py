"""
Dash app to do the data analysis 

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-10
"""
import os 
import pandas as pd

import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px

from model.TemperatureData import TemperatureData

# Initialize the Dash app
app = dash.Dash(__name__)

datapath = os.getcwd() + "/data/"  # Update this with the correct path
temperature_cases = [8, 37, 45, 55, 65, 75, 85]

# load temperature data 


app.layout = html.Div([
    html.H1("Temperature Data Analysis App"),
    html.Div([
        html.Div([
            html.H3("Temperature Data"),
            html.P("Select a temperature case"),
            dcc.Dropdown(options=["{:d} ℃".format(case) for case in temperature_cases], 
                         value=str(temperature_cases[0]),
            ),
        ], className="four columns"),
        html.Div([
            html.H3("Temperature Data"),
            dcc.Graph(id="temperature_graph"),
        ], className="eight columns"),
    ], className="row"),
])


# @app.callback(
#     Output("temperature_graph", "figure"),
#     Input("temperature_case", "value"),
# )
# def update_temperature_graph(temperature_case):
#     datapath_temperature = datapath + f"temperature_{temperature_case}.csv"
#     temperature_data = TemperatureData(datapath_temperature).df
#     fig = px.line(
#         temperature_data,
#         x="Time",
#         y="Temperature",
#         title=f"Temperature data for {temperature_case} ℃",
#     )
#     return fig

if __name__ == "__main__":
    app.run(debug=True)

