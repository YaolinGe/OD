import os

from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate

from controller.SingletonTemperatureData import SingletonTemperatureData


datapath = os.getcwd() + "/data/"  # Update this with the correct path


def add_timeseries_callback(app):
    @app.callback(
        Output("temperature_graph", "figure"),
        Input("temperature_case", "value"),
        Input("sensor", "value"),
        Input("slider", "value"),
        Input("slider_timewindow", "value"),
    )
    def update_graph(temperature_case, sensor, slider, slider_time_window):

        if temperature_case is None:
            raise PreventUpdate

        filename = datapath + f"temperature_{temperature_case}.csv"
        dataHandler = SingletonTemperatureData.get_instance(filename)
        data = dataHandler.df
        if sensor == "Sensor I":
            dataPlot = data[["ElapsedSeconds", "TemperatureSensorI"]]
        else:
            dataPlot = data[["ElapsedSeconds", "TemperatureSensorII"]]
        dataPlot = dataPlot.iloc[slider:]

        # s0, get time index of the current slider value
        time_index = int(slider / 100 * dataPlot.shape[0])
        time_indicator = dataPlot.iloc[time_index, 0]

        # cal1, calculate the window size and width
        window_half_width = int(slider_time_window / 100 * dataPlot.shape[0] / 2)
        ind_window_start = time_index - window_half_width if time_index - window_half_width >= 0 else 0
        ind_window_end = time_index + window_half_width if time_index + window_half_width <= dataPlot.shape[0] else \
            dataPlot.shape[0] - 1

        # cal2, get the data inside the window for later plotting
        x0 = dataPlot.iloc[ind_window_start, 0]
        x1 = dataPlot.iloc[ind_window_end, 0]
        data_in_window = dataPlot.iloc[ind_window_start:ind_window_end, 1]
        y0 = data_in_window.min()
        y1 = data_in_window.max()

        # cal3, calculate the 1st derivative of the data inside the window
        diff_data_in_window = data_in_window.diff()




        fig = make_subplots(rows=2, cols=2, specs=[[{"colspan": 2}, None], [{}, {}]], horizontal_spacing=.15)

        # p0, add the temperature time series
        fig.add_trace(go.Scatter(x=dataPlot["ElapsedSeconds"], y=dataPlot.iloc[:, 1], name=sensor), row=1, col=1)

        # p1, add the temperature time series only inside the window
        fig.add_trace(go.Scatter(x=data_in_window.index, y=data_in_window, name=sensor), row=2, col=1)

        # p2, add 1st derivative of the temperature time series only inside the window
        fig.add_trace(go.Scatter(x=diff_data_in_window.index, y=diff_data_in_window, name=sensor), row=2, col=2)

        # Update layout for the first subplot
        fig.update_xaxes(title_text="Elapsed Time (s)", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (℃)", row=1, col=1)

        # Update layout for the second subplot
        fig.update_xaxes(title_text="Elapsed Time (s)", row=2, col=1)
        fig.update_yaxes(title_text="TW", row=2, col=1)

        # Update layout for the third subplot
        fig.update_xaxes(title_text="Elapsed Time (s)", row=2, col=2)
        fig.update_yaxes(title_text="∂T/∂t", row=2, col=2)

        # Add other graphical elements like vertical line, shapes, etc.
        fig.add_vline(x=time_indicator, line_width=1, line_dash="solid", line_color="red", row=1, col=1)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="RoyalBlue", width=2), opacity=0.2,
                      fillcolor="LightSkyBlue")

        fig.update_layout(
            height=600,
            width=750,
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig
