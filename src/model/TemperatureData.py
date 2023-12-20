"""
Temperature data class to handle temperature data.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-12-20
"""
import os
import pandas as pd
import numpy as np


class TemperatureData:
    def __init__(self, filepath: str = None) -> None:
        self.validate_file(filepath)
        self.fileath = filepath
        self.load_data()

    def validate_file(self, filepath):
        if filepath is None:
            raise ValueError("Please provide a valid file name.")
        if not os.path.exists(filepath):
            raise FileNotFoundError("File not found.")
        if not filepath.endswith(".csv"):
            raise ValueError("Please provide a valid CSV file.")
        if not os.path.getsize(filepath) > 0:
            raise ValueError("The file is empty.")

    def load_data(self) -> None:
        self.df = pd.read_csv(self.fileath, sep=": ", header=None)
        if self.df.shape[1] != 3:
            raise ValueError("The file must have three columns.")
        self.df.columns = ['Timestamp', 'TemperatureSensorI', 'TemperatureSensorII']
        self.process_timestamps()
        self.calculate_elapsed_seconds()
        self.interpolate_temperatures()
        self.calculate_gradients()

    def process_timestamps(self):
        self.df['Timestamp'] = self.df['Timestamp'].str.replace('PM|AM', '', regex=True).str.replace('/', '-')
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'].apply(
            lambda x: '-'.join([x.split(' ')[0].split('-')[-1], x.split(' ')[0].split('-')[0], x.split(' ')[0].split('-')[1]]) + ' ' + x.split(' ')[1]
        ), format='%Y-%m-%d %H:%M:%S')

    def calculate_elapsed_seconds(self):
        elapsed_time = (self.df['Timestamp'] - self.df['Timestamp'][0]).dt.total_seconds()
        self.df['ElapsedSeconds'] = elapsed_time + self.df.groupby(elapsed_time).cumcount() * (1.0 / 12)

    def interpolate_temperatures(self):
        for sensor in ['TemperatureSensorI', 'TemperatureSensorII']:
            raw = (self.df[sensor] + 45) * 65535 / 175
            adc = raw / 65535
            resistance = adc * 40200 / (1 - adc)
            self.df[sensor] = (1 / ((np.log(resistance / 30000) / 3935) + (1 / 298.15))) - 273.15
            # smooth the sensor data so it is more smooth
            self.df[sensor] = self.df[sensor].rolling(5, min_periods=1).mean()
            # self.df[sensor] = self.df[sensor].interpolate(method='linear')

    def calculate_gradients(self):
        for sensor in ['TemperatureSensorI', 'TemperatureSensorII']:
            for i in range(1, 6):
                col_name = f'{sensor}_G{i}'
                prev_col = sensor if i == 1 else f'{sensor}_G{i-1}'
                self.df[col_name] = np.gradient(self.df[prev_col], self.df['ElapsedSeconds'])
        self.df = self.df.round(5)

    def smooth_data(self, timewindow: int = 0):
        for sensor in ['TemperatureSensorI', 'TemperatureSensorII']:
            self.df[sensor] = self.df[sensor].rolling(timewindow, min_periods=1).mean()
        self.calculate_gradients()


if __name__ == "__main__":
    td = TemperatureData()



