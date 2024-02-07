########################################################################################################################
#
########################################################################################################################
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('Qt5Agg')


########################################################################################################################
#
########################################################################################################################
class Plot:

    ####################################################################################################################
    def __init__(self, data_csv_file, marker_1=None, marker_2=None, plot_on_screen=True, plot_to_file=False):
        super().__init__()

        self._data_csv_file = data_csv_file
        self._marker_1 = marker_1
        self._marker_2 = marker_2
        self._plot_on_screen = plot_on_screen
        self._plot_to_file = plot_to_file

        self._fig = None

        self._df = pd.read_csv(self._data_csv_file, delimiter=',')

    ####################################################################################################################
    def _plot_to_screen(self, plot_block):

        if self._plot_on_screen:
            plt.show(block=plot_block)

        return

    ####################################################################################################################
    # def _plotting(self, window_title, title, y_label, x_label, plot_file_type, plot_block=False):
    def _plotting(self, window_title, title, y_label, x_label, plot_block=False):

        plt.title(title)
        # plt.legend()
        plt.grid()
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        plt.legend()

        # self._plot_to_file(plot_file_type)

        self._plot_to_screen(plot_block)

        if not plot_block:
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()

        return

    ####################################################################################################################
    def plot_sbc2_strain_gauge(self, title, plot_block):

        if hasattr(self._df, 'Timestamp_S') and hasattr(self._df, 'Data'):

            self._fig = plt.figure(num=title)

            plt.plot(self._df.Timestamp_S,  self._df.Data)

            self._plotting(self._data_csv_file, "SBC2: {0}".format(title), "Strain gauge", "Timestamp (S)", plot_block)

        return

    ####################################################################################################################
    def plot_sbc1_accelerometer(self, title, plot_block):

        if hasattr(self._df, 'Timestamp_S') and hasattr(self._df, 'X') and hasattr(self._df, 'Y') and hasattr(self._df, 'Z'):

            self._fig = plt.figure(num=title)

            plt.plot(self._df.Timestamp_S, self._df.X, label="X")
            plt.plot(self._df.Timestamp_S, self._df.Y, label="Y")
            plt.plot(self._df.Timestamp_S, self._df.Z, label="Z")

            self._plotting(self._data_csv_file, "SBC1: {0}".format(title), "Accelerometer (G)", "Timestamp (S)", plot_block)

        return

    ####################################################################################################################
    def plot_close(self):

        plt.close(self._fig)

        self._fig = None
