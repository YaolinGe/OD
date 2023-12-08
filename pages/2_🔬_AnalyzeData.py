"""
This page handles the data analysis process.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-08
"""
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class DataAnalyzer:

    def __init__(self) -> None:
        st.title("Data Analysis")
        self.df = None
        pass

    def show_data(self) -> None:
        """
        This function shows the data in the session state.
        """
        if 'data' in st.session_state:
            self.df = st.session_state['data']
            st.write("Data successfully loaded and processed!")
            # You can also display the data or some part of it here if you want
            st.dataframe(self.df.head())
        else:
            st.error("No data to show. Please load the data first.")

    def plot_data(self) -> None:
        """
        This function plots the desired properties against elapsed seconds using Plotly for interactive plots.
        """
        if self.df is not None:
            # Using the 'ElapsedSeconds' column for the x-axis
            elapsed_seconds = self.df['ElapsedSeconds']

            col1, col2 = st.columns(2)

            with col1: 
                # Creating a subplot for each property
                fig = make_subplots(rows=len(self.df.columns) - 1, cols=1, subplot_titles=self.df.columns[1:])

                # Iterate over the properties (excluding 'ElapsedSeconds')
                for i, col in enumerate(self.df.columns[1:], start=1):
                    fig.add_trace(go.Scatter(x=elapsed_seconds, y=self.df[col], mode='lines', name=col), row=i, col=1)

                fig.update_layout(height=800, width=1000, title_text="Time series", 
                                hovermode='x unified')
                st.plotly_chart(fig)
            with col2: 
                st.plotly_chart(fig)
        else:
            st.error("No data to plot. Please load the data first.")

    # def plot_data(self) -> None:
    #     """
    #     This function plots the desired properties against elapsed seconds.
    #     """
    #     if self.df is not None:
    #         # Using the 'ElapsedSeconds' column for the x-axis
    #         elapsed_seconds = self.df['ElapsedSeconds']

    #         # Plotting each property in a subplot
    #         fig, axs = plt.subplots(len(self.df.columns) - 1, 1, figsize=(10, 15))
    #         fig.tight_layout(pad=3.0)

    #         # Iterate over the properties (excluding 'ElapsedSeconds')
    #         for i, col in enumerate(self.df.columns[1:]):
    #             axs[i].plot(elapsed_seconds, self.df[col])
    #             axs[i].set_title(col)
    #             axs[i].set_xlabel('Elapsed Seconds')
    #             axs[i].set_ylabel(col)

    #         st.pyplot(fig)
    #     else:
    #         st.error("No data to plot. Please load the data first.")


if __name__ == "__main__":
    da = DataAnalyzer()
    da.show_data()
    da.plot_data()