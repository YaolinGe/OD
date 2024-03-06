import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os
import glob

## Sample files:
"""
SG-BT-CH0-V2-Dataset-2024-01-30-155131.txt
SG-BT-CH1-V2-Dataset-2024-01-30-155131.txt
SG-BT-CH2-V2-Dataset-2024-01-30-155131.txt
SG-BT-CH3-V2-Dataset-2024-01-30-155131.txt
ACC-Dataset-2024-01-30-155131.txt
"""

def get_latest_files():
    log_folder = "C:\\Log"
    starting_strings = ['SG-BT-CH0-V2-Dataset-', 'SG-BT-CH1-V2-Dataset-', 'SG-BT-CH2-V2-Dataset-',
                        'SG-BT-CH3-V2-Dataset-', 'ACC-Dataset-']
    latest_files = {}

    for starting_string in starting_strings:
        files = glob.glob(os.path.join(log_folder, starting_string + '*.txt'))
        if files:
            latest_file = max(files, key=os.path.getmtime)
            latest_files[starting_string] = latest_file

    return latest_files

latest_files = get_latest_files()
for file in latest_files.values():
    print(file)


# timestring = "2024-01-31-155131"
# channels = ["CH{:s}".format(ch) for ch in "0123"]
# files = ["SG-BT-{:s}-V2-Dataset-{:s}.txt".format(ch, timestring) for ch in channels]
# for file in files:
#     print(file)
# file_acc = "ACC-Dataset-{:s}.txt".format(timestring)

datasource_acc = ["x", "y", "z"]
maxlength_plot = 12 * 30

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Markdown("# OD Live Data Streaming"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 100,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    fig = make_subplots(rows=4, cols=2)
    latest_files = get_latest_files()
    files = [latest_files[key] for key in latest_files if 'ACC' not in key]
    file_acc = latest_files['ACC-Dataset-']
    all_files_empty = True

    for i, file in enumerate(files, start=1):
        try:
            data = np.genfromtxt(file, delimiter=',', skip_header=1)
            if data.size > 0:
                all_files_empty = False
                fig.add_trace(go.Scatter(x=data[-maxlength_plot:, 0],
                                         y=data[-maxlength_plot:, 1],
                                         mode='lines', name=file,
                                         showlegend=False), row=i, col=1)
                fig.update_yaxes(title_text=file[13:16], row=i, col=1)
        except ValueError:
            continue

    try:
        acc_data = np.genfromtxt(file_acc, delimiter=',', skip_header=1)
        if acc_data.size > 0:
            all_files_empty = False
            for i in range(3):
                fig.add_trace(go.Scatter(x=acc_data[-maxlength_plot:, 0],
                                         y=acc_data[-maxlength_plot:, i+1],
                                         mode='lines', name=datasource_acc[i], showlegend=False), row=i+1, col=2)
                fig.update_yaxes(title_text=datasource_acc[i], row=i+1, col=2)
    except ValueError:
        pass

    if all_files_empty:
        fig.add_annotation(text="Data is empty",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False)

    fig.update_layout(autosize=False, width=1560, height=720)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
