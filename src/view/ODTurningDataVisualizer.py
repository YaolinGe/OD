"""
ODTurningDataVisualizer shows the essential plots for the ODTurning data collected for ODTurning project.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-05
"""
import pandas as pd
import plotly.express as px
import streamlit as st


class ODTurningDataVisualizer:

    def __init__(self, dataFrame: pd.DataFrame = None) -> None:
        if dataFrame is None:
            raise ValueError("Please provide a valid data frame.")
        else:
            self.df = dataFrame

    def plot_item(self, y: str = "Deflection") -> None:
        """
        Use px to plot the line plot for both sensor I and sensor II
        """
        fig = px.line(self.df, x="ElapsedSeconds", y=y, title=f"{y}")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    tv = ODTurningDataVisualizer()
