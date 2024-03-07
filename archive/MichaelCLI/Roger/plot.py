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
    def __init__(self, data_csv_file1, data_csv_file2=None, data_csv_file3=None, data_csv_file4=None, marker_1=None, marker_2=None, plot_on_screen=True, plot_to_file=False):
        super().__init__()

        self._data_csv_file1 = data_csv_file1
        self._data_csv_file2 = data_csv_file2
        self._data_csv_file3 = data_csv_file3
        self._data_csv_file4 = data_csv_file4
        self._marker_1 = marker_1
        self._marker_2 = marker_2
        self._plot_on_screen = plot_on_screen
        self._plot_to_file = plot_to_file

        self._fig = None

        self._df1 = pd.read_csv(self._data_csv_file1, delimiter=',')
        self._df2 = None
        self._df3 = None
        self._df4 = None

        if data_csv_file2 is not None:
            self._df2 = pd.read_csv(self._data_csv_file2, delimiter=',')

        if data_csv_file3 is not None:
            self._df3 = pd.read_csv(self._data_csv_file3, delimiter=',')

        if data_csv_file4 is not None:
            self._df4 = pd.read_csv(self._data_csv_file4, delimiter=',')

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
    def plot_sbc2_strain_gauge(self, title, label, plot_block, no_of_average=16):

        if hasattr(self._df1, 'Timestamp_S') and hasattr(self._df1, 'Data'):

            self._fig = plt.figure(num=title)

            plt.plot(self._df1.Timestamp_S,  self._df1.Data, label=label, color='C1')

            if len(self._df1.Data) > no_of_average:

                self._df1['DataMean'] = self._df1['Data'].rolling(no_of_average).mean()
                plt.plot(self._df1.Timestamp_S, self._df1.DataMean, label=label + " RMEAN(" + str(no_of_average) + ")", color='C0')

                self._df1['DataEwm'] = self._df1['Data'].ewm(com=2).mean()
                plt.plot(self._df1.Timestamp_S, self._df1.DataEwm, label=label + " EMEAN(" + str(2) + ")", color='C2')

            self._plotting(self._data_csv_file1, "SBC2: {0}".format(title), "Strain gauge", "Timestamp (S)", plot_block)

        return

    ####################################################################################################################
    def plot_sbc2_strain_gauge_all(self, plot_block):

        self._fig = plt.figure(num="SBC2")

        if self._df2 is not None and hasattr(self._df1, 'Timestamp_S') and hasattr(self._df1, 'Data'):
            plt.plot(self._df1.Timestamp_S, self._df1.Data, label="CH0")

        if self._df2 is not None and hasattr(self._df2, 'Timestamp_S') and hasattr(self._df2, 'Data'):
            plt.plot(self._df2.Timestamp_S, self._df2.Data, label="CH1")

        if self._df3 is not None and hasattr(self._df3, 'Timestamp_S') and hasattr(self._df3, 'Data'):
            plt.plot(self._df3.Timestamp_S, self._df3.Data, label="CH2")

        if self._df4 is not None and hasattr(self._df4, 'Timestamp_S') and hasattr(self._df4, 'Data'):
            plt.plot(self._df4.Timestamp_S, self._df4.Data, label="CH3")

        self._plotting("SBC2", "SBC2", "Strain gauge", "Timestamp (S)", plot_block)

    ####################################################################################################################
    def plot_sbc1_accelerometer(self, title, plot_block):

        if hasattr(self._df1, 'Timestamp_S') and hasattr(self._df1, 'X') and hasattr(self._df1, 'Y') and hasattr(self._df1, 'Z'):

            self._fig = plt.figure(num=title)

            plt.plot(self._df1.Timestamp_S, self._df1.X, label="X")
            plt.plot(self._df1.Timestamp_S, self._df1.Y, label="Y")
            plt.plot(self._df1.Timestamp_S, self._df1.Z, label="Z")

            self._plotting(self._data_csv_file1, "SBC1: {0}".format(title), "Accelerometer (G or RAW)", "Timestamp (S)", plot_block)

        return

    ####################################################################################################################
    def plot_close(self):

        plt.close(self._fig)

        self._fig = None
