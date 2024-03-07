"""
This app is used to display the live view of the streaming data from the BLE device.

Methods:
    - Append stream data, and then view them directly in the browser using Dash.
    - The data is stored in a numpy array, and then displayed in the browser using Dash.
"""
import asyncio
import threading
import numpy as np
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from DataPool import DataPool


class LiveViewer:

    def __init__(self) -> None:

        self.app = Dash(__name__)
        self.configure_app()
        self.run_app()

    def append_strain_gauge_ch0(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch0 = np.append(self.strain_gauge_ch0, data_sg, axis=0)

    def append_strain_gauge_ch1(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch1 = np.append(self.strain_gauge_ch1, data_sg, axis=0)

    def append_strain_gauge_ch2(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch2 = np.append(self.strain_gauge_ch2, data_sg, axis=0)

    def append_strain_gauge_ch3(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch3 = np.append(self.strain_gauge_ch3, data_sg, axis=0)

    def append_accelerometer(self, log_string: str):
        data_acc = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.accelerometer = np.append(self.accelerometer, data_acc, axis=0)

    def configure_app(self) -> None:
        self.app.layout = html.Div([
            dcc.Markdown("# OD Live Data Streaming"),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=1 * 100,  # in milliseconds
                n_intervals=0
            )
        ])

        @self.app.callback(Output('live-update-graph', 'figure'),
                           [Input('interval-component', 'n_intervals')])
        def update_graph_live(n):
            if n == 0:
                raise PreventUpdate

            fig = make_subplots(rows=4, cols=2)

            if self.strain_gauge_ch0.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch0[:, 0])),
                                         y=self.strain_gauge_ch0[:, 0],
                                         mode='lines',
                                         name='Strain Gauge Ch0'),
                              row=1, col=1)

            if self.strain_gauge_ch1.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch1[:, 0])),
                                         y=self.strain_gauge_ch1[:, 0],
                                         mode='lines',
                                         name='Strain Gauge Ch1'),
                              row=2, col=1)

            if self.strain_gauge_ch2.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch2[:, 0])),
                                         y=self.strain_gauge_ch2[:, 0],
                                         mode='lines',
                                         name='Strain Gauge Ch2'),
                              row=3, col=1)

            if self.strain_gauge_ch3.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch3[:, 0])),
                                         y=self.strain_gauge_ch3[:, 0],
                                         mode='lines',
                                         name='Strain Gauge Ch3'),
                              row=4, col=1)

            if self.accelerometer.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer[:, 0])),
                                         y=self.accelerometer[:, 1],
                                         mode='lines',
                                         name='Accelerometer X'),
                              row=1, col=2)

                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer[:, 0])),
                                         y=self.accelerometer[:, 2],
                                         mode='lines',
                                         name='Accelerometer Y'),
                              row=2, col=2)

                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer[:, 0])),
                                         y=self.accelerometer[:, 3],
                                         mode='lines',
                                         name='Accelerometer Z'),
                              row=3, col=2)

            return fig

    def run_app(self) -> None:
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=start_loop, args=(new_loop,))
        t.start()

        new_loop.call_soon_threadsafe(self.app.run_server, debug=True, use_reloader=False)


if __name__ == "__main__":
    lv = LiveViewer()
