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
import plotly.graph_objects as go

from components.components import get_dashboard, get_timeslider
from layouts.layouts import update_layout
from model.TemperatureData import TemperatureData
from callbacks.callbacks import add_timeseries_callback

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

datapath = os.getcwd() + "/data/"  # Update this with the correct path
temperature_cases = [8, 37, 45, 55, 65, 75, 85]
temperature_case = temperature_cases[0]
filename = datapath + f"temperature_{temperature_case}.csv"
dataHandler = TemperatureData(filename)
data = dataHandler.df


dashboard = get_dashboard(temperature_cases)

update_layout(app, dashboard, get_timeslider())

add_timeseries_callback(app)


if __name__ == "__main__":
    app.run_server(debug=True, port=1000)



