import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots

timestring = "2024-01-31-155131"
channels = ["CH{:s}".format(ch) for ch in "0123"]
files = ["SG-BT-{:s}-V2-Dataset-{:s}.txt".format(ch, timestring) for ch in channels]
for file in files:
    print(file)
file_acc = "ACC-Dataset-{:s}.txt".format(timestring)
datasource_acc = ["x", "y", "z"]
maxlength_plot = 1000

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
    for i, file in enumerate(files, start=1):
        data = np.genfromtxt(file, delimiter=',', skip_header=1)
        fig.add_trace(go.Scatter(x=data[-maxlength_plot:, 0],
                                 y=data[-maxlength_plot:, 1],
                                 mode='lines', name=file,
                                 showlegend=False), row=i, col=1)
        fig.update_yaxes(title_text=file[6:9], row=i, col=1)

    acc_data = np.genfromtxt(file_acc, delimiter=',', skip_header=1)
    for i in range(3):
        fig.add_trace(go.Scatter(x=acc_data[-maxlength_plot:, 0],
                                 y=acc_data[-maxlength_plot:, i+1],
                                 mode='lines', name=datasource_acc[i], showlegend=False), row=i+1, col=2)
        fig.update_yaxes(title_text=datasource_acc[i], row=i+1, col=2)
    fig.update_layout(autosize=False, width=1560, height=720)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
