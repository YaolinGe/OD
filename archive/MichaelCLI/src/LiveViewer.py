"""
This app is used to display the live view of the streaming data from the BLE device.

Methods:
    - Append stream data, and then view them directly in the browser using Dash.
    - The data is stored in a numpy array, and then displayed in the browser using Dash.
"""
import numpy as np
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from DataStreamSubscriber import DataStreamSubscriber


class LiveViewer:

    def __init__(self) -> None:
        self.data_stream_subscriber = DataStreamSubscriber()
        self.data_stream_subscriber.start_subscriber_thread()
        self.app = Dash(__name__)
        self.configure_app()

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

            data_arrays = self.data_stream_subscriber.data_arrays
            self.strain_gauge_ch0 = data_arrays["strain_gauge_ch0"]
            self.strain_gauge_ch1 = data_arrays["strain_gauge_ch1"]
            self.strain_gauge_ch2 = data_arrays["strain_gauge_ch2"]
            self.strain_gauge_ch3 = data_arrays["strain_gauge_ch3"]
            self.accelerometer_raw = data_arrays["accelerometer_raw"]

            fig = make_subplots(rows=4, cols=2)

            if self.strain_gauge_ch0.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch0[:, 0])),
                                         y=self.strain_gauge_ch0[:, 1],
                                         mode='lines',
                                         name='Strain Gauge Ch0',
                                         showlegend=False),
                              row=1, col=1)

            if self.strain_gauge_ch1.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch1[:, 0])),
                                         y=self.strain_gauge_ch1[:, 1],
                                         mode='lines',
                                         name='Strain Gauge Ch1',
                                         showlegend=False),
                              row=2, col=1)

            if self.strain_gauge_ch2.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch2[:, 0])),
                                         y=self.strain_gauge_ch2[:, 1],
                                         mode='lines',
                                         name='Strain Gauge Ch2',
                                         showlegend=False),
                              row=3, col=1)

            if self.strain_gauge_ch3.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.strain_gauge_ch3[:, 0])),
                                         y=self.strain_gauge_ch3[:, 1],
                                         mode='lines',
                                         name='Strain Gauge Ch3',
                                         showlegend=False),
                              row=4, col=1)

            if self.accelerometer_raw.size > 0:
                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer_raw[:, 0])),
                                         y=self.accelerometer_raw[:, 1],
                                         mode='lines',
                                         name='Accelerometer X',
                                         showlegend=False),
                              row=1, col=2)

                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer_raw[:, 0])),
                                         y=self.accelerometer_raw[:, 2],
                                         mode='lines',
                                         name='Accelerometer Y',
                                         showlegend=False),
                              row=2, col=2)

                fig.add_trace(go.Scatter(x=np.arange(len(self.accelerometer_raw[:, 0])),
                                         y=self.accelerometer_raw[:, 3],
                                         mode='lines',
                                         name='Accelerometer Z',
                                         showlegend=False),
                              row=3, col=2)

            # add xlabel, ylabel to mark the corresponding sensor name and channel name for each subplot, such as if data is self.strain_gauge_ch0, then ylabel should be "CH0" and xlabel should be Time [seconds]
            fig.update_yaxes(title_text="CH0", row=1, col=1)
            fig.update_yaxes(title_text="CH1", row=2, col=1)
            fig.update_yaxes(title_text="CH2", row=3, col=1)
            fig.update_yaxes(title_text="CH3", row=4, col=1)
            fig.update_yaxes(title_text="ACC X", row=1, col=2)
            fig.update_yaxes(title_text="ACC Y", row=2, col=2)
            fig.update_yaxes(title_text="ACC Z", row=3, col=2)
            fig.update_xaxes(title_text="Time [seconds]", row=4, col=2)

            fig.update_layout(height=800, width=1400)

            return fig


if __name__ == "__main__":
    lv = LiveViewer()
    lv.app.run_server(debug=True, use_reloader=False)
