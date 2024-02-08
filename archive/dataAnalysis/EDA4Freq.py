"""
This file contains the exploratory data analysis (EDA) for the frequency of the project.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-27

The EDA is used to explore the test data generated during OD turning project.

Data attributes:
- data: two columns containing timestamp and adc values
    - timestamp: timestamp
    - adc: adc values
"""
from src.TxtData import TxtData
from src.usr_func.checkfolder import checkfolder
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from tqdm import tqdm
from joblib import Parallel, delayed


mpl.rcParams['font.size'] = 20
mpl.rcParams['font.family'] = 'Times New Roman'


class EDA:

    def __init__(self) -> None:
        self.figpath = os.path.join(os.getcwd(), "fig", "OD", "Freq")
        checkfolder(self.figpath)
        self.folderpath = os.path.join(os.getcwd(), "data")
        self.files = os.listdir(self.folderpath)
        for file in self.files:
            if file.endswith(".txt"):
                filepath = os.path.join(self.folderpath, file)
                print("Making plots for file: ", filepath)
                # self.make_plot_for_file(filepath)
                self.make_peak2peak_plot(filepath)

    def make_peak2peak_plot(self, filepath: str = None) -> None:
        df = TxtData(filepath).data
        adc = df['Data'].to_numpy()
        timestamp = df['Timestamp_S'].to_numpy()
        """ make a histogram plot using sns, and use kde estimation to find out the distribution
        and find out the min and max and peak to peak """
        plt.figure(figsize=(10, 8))
        sns.distplot(adc, hist=True, kde=True,
                        bins=int(180 / 5), color='darkblue',
                        hist_kws={'edgecolor': 'black'},
                        kde_kws={'linewidth': 4})
        plt.xlabel("ADC")
        plt.ylabel("Density")
        plt.title("Histogram of ADC")
        plt.show()
        # plt.savefig(self.figpath + "/hist.png", dpi=300)

        df
        pass

    def make_plot_for_file(self, filepath: str = None):
        """
        Make the plots for one file
        """
        # s0, load the data
        df = TxtData(filepath).data
        adc = df['Data'].to_numpy()
        timestamp = df['Timestamp_S'].to_numpy()
        sampling_interval = np.mean(np.diff(timestamp))
        sampling_rate = 1 / sampling_interval
        print(f"Sampling rate: {sampling_rate} Hz")
        print(f"Sampling interval: {sampling_interval} seconds")
        print(f"Length of the data: {len(adc)}")

        XLIM = [timestamp[0], timestamp[-1]]
        YLIM = [np.min(adc), np.max(adc)]

        def plot_frequency4signal(ind_start: int = 0, ind_end: int = 100, cnt: int = 0):
            """
            This function is used to plot the original signal and its corresponding frequency spectrum.

            :param ind_start: int, the starting index of the signal
            :param ind_end: int, the ending index of the signal
            :return: None
            """
            signal = adc[ind_start:ind_end]
            f_signal = np.fft.fft(signal)
            xf_signal = np.fft.fftfreq(len(signal), sampling_interval)
            data_df = pd.DataFrame({"Frequency": xf_signal, "Power": np.log(np.abs(f_signal))})

            fig = plt.figure(figsize=(20, 16))
            gs = GridSpec(2, 2, figure=fig)

            # f0, plot the original time series data with full span on the first row
            # also include a small rectangle to highlight the selected section
            ax0 = fig.add_subplot(gs[0, :])
            ax0.plot(timestamp, adc, 'k-')
            ax0.plot(timestamp[ind_start:ind_end], adc[ind_start:ind_end], 'r-')
            ylim = [-6000, 6000] + np.mean(signal)
            rect = mpl.patches.Rectangle((timestamp[ind_start], ylim[0]), timestamp[ind_end] - timestamp[ind_start],
                                         ylim[1] - ylim[0], linewidth=4, edgecolor='g', facecolor='none')
            ax0.add_patch(rect)
            ax0.set_xlim(XLIM)
            ax0.set_ylim(YLIM)
            ax0.set_xlabel("Time, [s]")
            ax0.set_ylabel("ADC")
            ax0.set_title("Original signal")
            ax0.grid(True, which='both', axis='both')

            # f1, plot the original signal, extend it a bit longer and add the window to illustrate the highlighted section
            ax0 = fig.add_subplot(gs[1, 0])
            ax0.plot(timestamp[ind_start:ind_end], adc[ind_start:ind_end], 'r-')
            ax0.set_xlim(timestamp[ind_start], timestamp[ind_end])
            ax0.set_ylim(YLIM)
            ax0.set_xlabel("Time, [s]")
            ax0.set_ylabel("ADC")
            ax0.set_title("Selected raw signal")
            ax0.grid(True, which='both', axis='both')

            # f2, plot the frequency spectrum
            ax1 = fig.add_subplot(gs[1, 1])
            sns.lineplot(x="Frequency", y="Power", data=data_df, color="k", ax=ax1)
            plt.xlabel("Frequency, [Hz]")
            plt.ylabel("SNR, dB")
            plt.xlim(0, 250)
            plt.ylim(0, 20)
            ax1.grid(True, which='both', axis='both')

            plt.savefig(self.figpath + "/P_{:03d}.png".format(cnt), dpi=300)
            plt.close("all")
            # plt.show()
            pass

        time_window = 5000
        step = 500
        for i in tqdm(range(0, len(adc), step)):
            if i + step < len(adc):
                plot_frequency4signal(i, i + time_window, int(i // step))
            else:
                plot_frequency4signal(i, -1, int(i // step))


if __name__ == "__main__":
    e = EDA()
