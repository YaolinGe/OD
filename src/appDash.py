"""
Dash app to do the data analysis for Bobben temperature research project.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-10
"""
import os
import pandas as pd

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

from model.TemperatureData import TemperatureData
from controller.SingletonTemperatureData import SingletonTemperatureData

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

datapath = os.getcwd() + "/data/"  # Update this with the correct path
temperature_cases = [8, 37, 45, 55, 65, 75, 85]
temperature_case = temperature_cases[0]
filename = datapath + f"temperature_{temperature_case}.csv"
dataHandler = TemperatureData(filename)
data = dataHandler.df

app.layout = html.Div([
    html.H1("Temperature Data Analysis App", style={"textAlign": "center"}),
    html.Div([
        # Control panel with 1/3 width
        html.Div([
            html.H3("Control Dashboard"),

            html.Br(),
            html.P("Select a temperature ℃"),
            dcc.Dropdown(id="temperature_case",
                         options=[{"label": "{:d} ℃".format(case), "value": case} for case
                                  in temperature_cases],
                         value=temperature_cases[0]),

            html.Br(),
            html.P("Select a sensor "),
            dcc.RadioItems(options=['Sensor I', 'Sensor II'], value="Sensor II", id="sensor"),

            html.Br(),
            html.P("Select a time window"),
            dcc.Slider(id="slider_timewindow", min=0, max=100, step=10, value=0),

            html.Br(),
            html.P("Time slider"),
            dcc.Slider(id="slider", min=0, max=100, marks=None, value=0),
        ], className="four columns"),  # 1/3 of the space
        # Visualization panel with 2/3 width
        html.Div([
            html.H3("Data Visualization"),
            dcc.Graph(id="temperature_graph"),
            # dcc.Graph(id="temperature_gradient_on_window"),
        ], className="eight columns"),  # 2/3 of the space
    ], className="row"),
])


@callback(
    Output("temperature_graph", "figure"),
    Input("temperature_case", "value"),
    Input("sensor", "value"),
    Input("slider", "value"),
)
def update_graph(temperature_case, sensor, slider):
    filename = datapath + f"temperature_{temperature_case}.csv"
    dataHandler = SingletonTemperatureData.get_instance(filename)
    data = dataHandler.df
    if sensor == "Sensor I":
        dataPlot = data[["ElapsedSeconds", "TemperatureSensorI"]]
    else:
        dataPlot = data[["ElapsedSeconds", "TemperatureSensorII"]]
    dataPlot = dataPlot.iloc[slider:]
    fig = px.line(dataPlot, x="ElapsedSeconds", y=dataPlot.columns[1], title="Temperature vs. Time")
    time_index = int(slider / 100 * dataPlot.shape[0])
    time_indicator = dataPlot.iloc[time_index, 0]
    fig.add_vline(x=time_indicator, line_width=1, line_dash="solid", line_color="red")
    return fig

# @callback(
#     Output("temperature_gradient_on_window", "figure"),
#     Input("temperature_case", "value"),
#     Input("sensor", "value"),
#     Input("slider", "value"),
# )
# def update_gradient_graph(temperature_case, sensor, slider):
#     filename = datapath + f"temperature_{temperature_case}.csv"
#     dataHandler = SingletonTemperatureData.get_instance(filename)
#     data = dataHandler.df
#     if sensor == "Sensor I":
#         dataPlot = data[["ElapsedSeconds", "TemperatureSensorI"]]
#     else:
#         dataPlot = data[["ElapsedSeconds", "TemperatureSensorII"]]
#     dataPlot = dataPlot.iloc[slider:]
#     fig = px.line(dataPlot, x="ElapsedSeconds", y=dataPlot.columns[1], title="Temperature vs. Time")
#     return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=1000)
