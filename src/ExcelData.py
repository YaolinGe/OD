"""
OD Turning Data object 

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-24

The data object is used to extract the OD turning data from the raw data saved in xlsx files. It has several sheet names, including:
- Deflection: deflection data of the OD turning test 
- Load: load data of the OD turning test
- Temperature: temperature data of the OD turning test
- Rawdata: raw data of the OD turning test
"""
import os
import pandas as pd
from src.usr_func.timestamp2seconds import timestamp2seconds
from scipy.interpolate import interp1d
import numpy as np


class ExcelData:

    def __init__(self, filepath: str = None) -> None:
        if filepath is None:
            raise ValueError("Please provide a valid file name.")
        else:
            if not os.path.exists(filepath):
                raise FileNotFoundError("File not found.")
            else:
                if not filepath.endswith(".xlsx"):
                    raise ValueError("Please provide a valid file name. It has to be a xlsx file.")
                else:
                    self.filepath = filepath

        self.df_deflection = self.load_deflection_data()
        self.df_load = self.load_data4load()
        self.df_temperature = self.load_data4temperature()
        self.df_rawdata = self.load_data4rawdata()
        self.df_sync = self.synchronize_data()

    def load_deflection_data(self) -> pd.DataFrame:
        df = pd.read_excel(self.filepath, sheet_name="Deflection")
        df = df.loc[:, ['Key', 'Value']]
        df.columns = ["ElapsedSeconds", "Deflection"]
        df['ElapsedSeconds'] = df['ElapsedSeconds'].apply(timestamp2seconds)
        return df

    def load_data4load(self) -> pd.DataFrame:
        df = pd.read_excel(self.filepath, sheet_name="Load")
        df = df.loc[:, ['Key', 'Value']]
        df.columns = ["ElapsedSeconds", "Load"]
        df['ElapsedSeconds'] = df['ElapsedSeconds'].apply(timestamp2seconds)
        return df

    def load_data4temperature(self) -> pd.DataFrame:
        df = pd.read_excel(self.filepath, sheet_name="Temperature")
        df = df.loc[:, ['Key', 'Value']]
        df.columns = ["ElapsedSeconds", "Temperature"]
        df['ElapsedSeconds'] = df['ElapsedSeconds'].apply(timestamp2seconds)
        return df

    def load_data4rawdata(self) -> pd.DataFrame:
        """
        Load the ADC raw data from the excel file.
        """
        df = pd.read_excel(self.filepath, sheet_name="Rawdata")
        df = df.loc[:, ['TotalSeconds', 'OD-TurningStrainRaw0', 'OD-TurningStrainRaw1']]
        df.columns = ["ElapsedSeconds", "StrainGauge1", "StrainGauge2"]
        df = df[df['ElapsedSeconds'] > 0]
        return df

    def synchronize_data(self) -> pd.DataFrame:
        """
        Synchronize all the data according to their time stamps.

        Methodology:
        - Find the minimum and maximum time stamps
        - Create a time series with 1 ms interval
        - Interpolate the data to the time series
        - Merge the data into one dataframe

        """
        df_deflection = self.df_deflection
        df_load = self.df_load
        df_temperature = self.df_temperature
        df_rawdata = self.df_rawdata

        # Find the minimum and maximum time stamps
        min_time = min(df_deflection['ElapsedSeconds'].min(), df_load['ElapsedSeconds'].min(),
                       df_temperature['ElapsedSeconds'].min(), df_rawdata['ElapsedSeconds'].min())
        max_time = max(df_deflection['ElapsedSeconds'].max(), df_load['ElapsedSeconds'].max(),
                       df_temperature['ElapsedSeconds'].max(), df_rawdata['ElapsedSeconds'].max())

        # Create a time series with 100 ms interval
        time_series = np.arange(min_time, max_time, .1)

        # Function to interpolate using scipy
        def interpolate_to_common_time_series(df, time_series):
            try:
                # Try cubic interpolation first
                interpolator = interp1d(df['ElapsedSeconds'], df.iloc[:, 1], kind='cubic', bounds_error=False,
                                        fill_value="extrapolate")
                interpolated_values = interpolator(time_series)
            except ValueError as e:
                print("Cubic interpolation failed:", e)
                print("Falling back to linear interpolation.")
                # Fall back to linear interpolation
                interpolator = interp1d(df['ElapsedSeconds'], df.iloc[:, 1], kind='linear', bounds_error=False,
                                        fill_value="extrapolate")
                interpolated_values = interpolator(time_series)

            # Create a new DataFrame with the interpolated values
            return pd.DataFrame({df.columns[0]: time_series, df.columns[1]: interpolated_values})

        # Interpolate the data to the time series
        df_deflection = interpolate_to_common_time_series(df_deflection, time_series)
        df_load = interpolate_to_common_time_series(df_load, time_series)
        df_temperature = interpolate_to_common_time_series(df_temperature, time_series)
        df_rawdata1 = interpolate_to_common_time_series(df_rawdata.iloc[:, :2], time_series)
        df_rawdata2 = interpolate_to_common_time_series(df_rawdata.iloc[:, [0, 2]], time_series)

        # Merge the data into one dataframe
        df = pd.merge(df_deflection, df_load, on='ElapsedSeconds')
        df = pd.merge(df, df_temperature, on='ElapsedSeconds')
        df = pd.merge(df, df_rawdata1, on='ElapsedSeconds')
        df = pd.merge(df, df_rawdata2, on='ElapsedSeconds')
        df.columns = ["ElapsedSeconds", "Deflection", "Load", "Temperature", "StrainGauge1", "StrainGauge2"]
        return df


if __name__ == "__main__": 
    d = ExcelData()
    