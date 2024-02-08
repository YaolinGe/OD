import os 
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from seq_ble_cli import main 


if __name__ == "__main__": 
    main()


# read file_start_date and file_start_time from "file_start_date_time.txt"
# file_start_date_time = open("file_start_date_time.txt", "r")
# file_start_date_time = file_start_date_time.read()
# file_start_date_time = file_start_date_time.split("\n")
# file_start_date = file_start_date_time[0]
# file_start_time = file_start_date_time[1]

# file_start_string = file_start_date + "-" + file_start_time

# file_names = []
# for file in os.listdir():
#     if file_start_string in file:
#         file_names.append(file)

# file_names.sort()

# channels = ["CH0", "CH1", "CH2", "CH3"]



# app = Dash(__name__)


# app.layout = html.Div([
#     html.H1('Hello Roger App'),
#     html.Div('Dash: Web Dashboards with Python'),

#     html.Button("Update", id="update-button", n_clicks=0),

#     html.Div(
#         id = "graph",
#     )
# ])

# @app.callback(
#     Output("graph", "children"),
#     Input("update-button", "n_clicks"),
# )
# def update_graph(n_clicks):

#     # Create a subplot figure with 2 rows and 2 columns
#     fig = make_subplots(rows=2, cols=2, subplot_titles=channels)

#     # Track the current subplot position
#     subplot_pos = [(1, 1), (1, 2), (2, 1), (2, 2)]

#     for i, channel in enumerate(channels):
#         for file in file_names:
#             if channel in file:
#                 file_name = file
#                 df = pd.read_csv(file_name, sep=",")
#                 df.columns = ["time", "value"]
                
#                 # Add trace to the current subplot
#                 row, col = subplot_pos[i]
#                 fig.add_trace(
#                     go.Scatter(x=df["time"], y=df["value"], name=channel),
#                     row=row, col=col
#                 )

#     # Update layout once, outside the loop
#     fig.update_layout(
#         title="Channel Data",
#         xaxis_title="Time",
#         yaxis_title="Value",
#         legend_title="Channels",
#         font=dict(
#             family="Courier New, monospace",
#             size=18,
#             color="RebeccaPurple"
#         )
#     )

#     # Optionally, update xaxis and yaxis titles for each subplot if needed
#     for i in range(1, 5):
#         fig.update_xaxes(title_text="Time", row=i//3+1, col=i%2+1)
#         fig.update_yaxes(title_text="Value", row=i//3+1, col=i%2+1)

   
#     return dcc.Graph(figure=fig)



# if __name__ == '__main__':
#     app.run_server(debug=True, port=1234)

