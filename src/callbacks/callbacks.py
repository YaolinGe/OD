import os

from dash.dependencies import Input, Output
import plotly.graph_objs as go

from controller.SingletonTemperatureData import SingletonTemperatureData


datapath = os.getcwd() + "/data/"  # Update this with the correct path


def add_callbacks(app):
    @app.callback(
        Output("temperature_graph", "figure"),
        Input("temperature_case", "value"),
        Input("sensor", "value"),
        Input("slider", "value"),
        Input("slider_timewindow", "value"),
    )
    def update_graph(temperature_case, sensor, slider, slider_time_window):
        filename = datapath + f"temperature_{temperature_case}.csv"
        dataHandler = SingletonTemperatureData.get_instance(filename)
        data = dataHandler.df
        if sensor == "Sensor I":
            dataPlot = data[["ElapsedSeconds", "TemperatureSensorI"]]
        else:
            dataPlot = data[["ElapsedSeconds", "TemperatureSensorII"]]
        dataPlot = dataPlot.iloc[slider:]
        fig = go.Figure(go.Scatter(x=dataPlot["ElapsedSeconds"], y=dataPlot.iloc[:, 1]))
        time_index = int(slider / 100 * dataPlot.shape[0])
        time_indicator = dataPlot.iloc[time_index, 0]
        fig.add_vline(x=time_indicator, line_width=1, line_dash="solid", line_color="red")
        window_half_width = int(slider_time_window / 100 * dataPlot.shape[0] / 2)
        ind_window_start = time_index - window_half_width if time_index - window_half_width >= 0 else 0
        ind_window_end = time_index + window_half_width if time_index + window_half_width <= dataPlot.shape[0] else \
            dataPlot.shape[0] - 1
        x0 = dataPlot.iloc[ind_window_start, 0]
        x1 = dataPlot.iloc[ind_window_end, 0]
        data_in_window = dataPlot.iloc[ind_window_start:ind_window_end, 1]
        y0 = data_in_window.min()
        y1 = data_in_window.max()
        fig.add_shape(type="rect",
                      x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(
                          color="RoyalBlue",
                          width=2,
                      ),
                      opacity=0.2,
                      fillcolor="LightSkyBlue",
                      )
        return fig