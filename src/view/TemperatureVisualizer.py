"""
TemperatureVisualizer shows the essential plots for the temperature data collected for Bobben

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-20
"""
import pandas as pd
import plotly.express as px
import streamlit as st


class TemperatureVisualizer: 

    def __init__(self, dataFrame: pd.DataFrame=None) -> None:
        if dataFrame is None:
            raise ValueError("Please provide a valid data frame.")
        else:
            self.df = dataFrame

    def plot_temperature(self, y: str = "TemperatureSensorI") -> None:
        """
        Use px to plot the line plot for both sensor I and sensor II
        """
        fig = px.line(self.df, x="ElapsedSeconds", y=y, title=f"{y}")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__": 
    tv = TemperatureVisualizer()
    