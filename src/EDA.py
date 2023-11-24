"""
This file contains the exploratory data analysis (EDA) for the project.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-24

The EDA is used to explore the test data generated during OD turning project.

Data attributes:
- df_sync: synchronized data of the OD turning test
    - ElapsedSeconds: elapsed seconds
    - Deflection: deflection
    - Load: load
    - Temperature: temperature
    - StrainGauge1: strain gauge 1
    - StrainGauge2: strain gauge 2
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.Data import Data
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from tqdm import tqdm
from joblib import Parallel, delayed


mpl.rcParams['font.size'] = 20
mpl.rcParams['font.family'] = 'Times New Roman'


class EDA:

    def __init__(self) -> None:
        self.figpath = os.path.join(os.getcwd(), "fig")
        self.folderpath = os.path.join(os.getcwd(), "data")
        self.files = os.listdir(self.folderpath)

    def make_plots_for_all_files(self) -> None:
        """
        Make the plots for each file
        """
        filepath = os.path.join(self.folderpath, self.files[1])
        self.make_plot_for_file(filepath)
        pass

    def make_plot_for_file(self, filepath: str = None) -> None:
        """
        Visualize the data in one figure, and make animation with a time window
        to show the variation over time when different parameter changed!
        """
        df = Data(filepath).df_sync
        figpath = os.path.join(self.figpath, os.path.basename(filepath).split(".")[0])
        def make_subplot(ax, value, title, step: int = -1) -> None:
            ax.plot(df['ElapsedSeconds'][:step], df[value][:step], 'k-')
            ax.set_ylabel(value)
            ax.set_title(title)
            ax.set_xlim([df['ElapsedSeconds'].min(), df['ElapsedSeconds'].max()])
            ax.set_ylim([df[value].min() * 0.999, df[value].max() * 1.001])
            ax.xaxis.grid(True, which='major')
            ax.yaxis.grid(True, which='major')

        items = ['Deflection', 'Load', 'Temperature', 'StrainGauge1', 'StrainGauge2']

        def make_subplot_for_timestep(step: int = 0):
            fig = plt.figure(figsize=(15, 25))
            gs = GridSpec(5, 1, figure=fig)
            for i in range(5):
                ax = fig.add_subplot(gs[i, 0])
                make_subplot(ax, items[i], items[i], step)
            plt.xlabel("Elapsed Seconds")
            plt.savefig(os.path.join(figpath, "P_{:03d}.png".format(step)))
            plt.close("all")

        for i in range(10):
        # for i in tqdm(range(df.shape[0])):
            make_subplot_for_timestep(i)


if __name__ == "__main__":
    e = EDA()
