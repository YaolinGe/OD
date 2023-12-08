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
from src.usr_func.checkfolder import checkfolder
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.ExcelData import ExcelData
import matplotlib as mpl
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from tqdm import tqdm
from joblib import Parallel, delayed


mpl.rcParams['font.size'] = 20
mpl.rcParams['font.family'] = 'Times New Roman'


class EDA:

    def __init__(self) -> None:
        self.figpath = os.path.join(os.getcwd(), "fig", "Sync")
        self.folderpath = os.path.join(os.getcwd(), "data")
        self.files = os.listdir(self.folderpath)

    def make_subplot(self, ax_container, df, value, title, step: int = -1) -> None:
        fig = ax_container.figure
        gs = GridSpecFromSubplotSpec(nrows=1, ncols=4, subplot_spec=ax_container.get_subplotspec())

        # s0, set up the index for time window
        time_window = 100
        ind_start = max(0, step - time_window // 2)
        ind_end = min(df.shape[0], step + time_window // 2)

        # p1, make plot for timeseries data
        ax_time = fig.add_subplot(gs[0, :2])
        ax_time.plot(df['ElapsedSeconds'][:step], df[value][:step], 'k-')
        ax_time.plot(df['ElapsedSeconds'][ind_start:ind_end], df[value][ind_start:ind_end], 'r-')
        data_box = df.loc[:, ['ElapsedSeconds', value]].iloc[ind_start:ind_end, :]
        rect = mpl.patches.Rectangle((data_box['ElapsedSeconds'].min(), data_box[value].min() * 0.999),
                                        data_box['ElapsedSeconds'].max() - data_box['ElapsedSeconds'].min(),
                                        data_box[value].max() * 1.001 - data_box[value].min() * 0.999, linewidth=2,
                                        edgecolor='g', facecolor='none')
        """ add text on the topright corner to show the peak-peak value """
        ax_time.text(0.95, 0.95, "Peak-peak: {:.2f}".format(data_box[value].max() - data_box[value].min()),
                        horizontalalignment='right', verticalalignment='top', transform=ax_time.transAxes)
        ax_time.text(0.95, 0.90, "Mean: {:.2f}".format(data_box[value].mean()),
                        horizontalalignment='right', verticalalignment='top', transform=ax_time.transAxes)
        ax_time.text(0.95, 0.85, "Std: {:.2f}".format(data_box[value].std()),
                        horizontalalignment='right', verticalalignment='top', transform=ax_time.transAxes)

        ax_time.add_patch(rect)
        ax_time.set_ylabel(value)
        ax_time.set_title(title)
        ax_time.set_xlim([df['ElapsedSeconds'].min(), df['ElapsedSeconds'].max()])
        ax_time.set_ylim([df[value].min() * 0.999, df[value].max() * 1.001])
        ax_time.xaxis.grid(True, which='major')
        ax_time.yaxis.grid(True, which='major')
        ax_time.axvline(df['ElapsedSeconds'][step], color='r', linestyle='--', linewidth=2)

        # p2, make the histogram plot
        ax_hist = fig.add_subplot(gs[0, 2])
        df_hist_window = df.loc[:, ['ElapsedSeconds', value]].iloc[ind_start:ind_end, :]
        df_hist_total = df.loc[:, ['ElapsedSeconds', value]].iloc[:step, :]
        sns.kdeplot(data=df_hist_total, y=value, color='k', fill=True, ax=ax_hist)
        sns.kdeplot(data=df_hist_window, y=value, color='r', fill=True, ax=ax_hist)
        ax_hist.axhline(df[value][step], color='g', linestyle='--', linewidth=2)
        ax_hist.set_ylabel(value)
        ax_hist.set_xlabel("Density")
        ax_hist.set_title("Histogram of {}".format(value))
        ax_hist.set_ylim([df[value].min() * 0.999, df[value].max() * 1.001])
        ax_hist.yaxis.grid(True, which='major')
        ax_hist.xaxis.grid(True, which='major')

        # p3, make fft plot for the timewindow data
        ax_fft = fig.add_subplot(gs[0, 3])
        timestamp = df['ElapsedSeconds'].iloc[ind_start:ind_end].to_numpy()
        signal = df[value].iloc[ind_start:ind_end].to_numpy()
        sampling_interval = np.mean(np.diff(timestamp))
        sampling_rate = 1 / sampling_interval
        f_signal = np.fft.fft(signal)
        xf_signal = np.fft.fftfreq(len(signal), sampling_interval)
        data_df = pd.DataFrame({"Frequency": xf_signal, "Power": np.log(np.abs(f_signal))})
        sns.lineplot(x="Frequency", y="Power", data=data_df, color="k", ax=ax_fft)
        ax_fft.set_xlabel("Frequency, [Hz]")
        ax_fft.set_ylabel("SNR, dB")
        ax_fft.set_title("Power spectrum of {}".format(value))
        ax_fft.set_xlim(0, 5)
        ax_fft.set_ylim(0, 20)
        ax_fft.xaxis.grid(True, which='major')
        ax_fft.yaxis.grid(True, which='major')

    def make_subplot_for_timestep(self, df, figpath, step: int = 0):
        fig = plt.figure(figsize=(35, 40))
        gs_main = GridSpec(5, 1, figure=fig)
        items = ['Deflection', 'Load', 'Temperature', 'StrainGauge1', 'StrainGauge2']

        for i, item in enumerate(items):
            ax_container = fig.add_subplot(gs_main[i, :])
            ax_container.tick_params(labelleft=False, labelbottom=False)
            ax_container.spines['top'].set_visible(False)
            ax_container.spines['right'].set_visible(False)
            ax_container.spines['bottom'].set_visible(False)
            ax_container.spines['left'].set_visible(False)
            self.make_subplot(ax_container, df, item, item, step)

        plt.savefig(os.path.join(figpath, "P_{:03d}.png".format(step)), dpi=100)
        plt.close(fig)

    def make_plots_for_all_files(self):
        # Only read the file once per file
        for file in self.files:
            if file.endswith(".xlsx"):
                filepath = os.path.join(self.folderpath, file)
                print("Making plots for file: ", filepath)
                df = ExcelData(filepath).df_sync  # Read file once
                figpath = os.path.join(self.figpath, os.path.basename(filepath).split(".")[0])
                checkfolder(figpath)

                # Parallel processing for each timestep
                Parallel(n_jobs=15)(
                    delayed(self.make_subplot_for_timestep)(df, figpath, i) for i in tqdm(range(df.shape[0])))


if __name__ == "__main__":
    plt.rcParams['font.size'] = 20
    plt.rcParams['font.family'] = 'Times New Roman'
    e = EDA()
    e.make_plots_for_all_files()

