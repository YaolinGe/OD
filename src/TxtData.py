"""
OD Turning Data object

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-27

The data object is used to extract the OD turning data from the raw data saved in txt file.
"""

import os
import pandas as pd
from src.usr_func.timestamp2seconds import timestamp2seconds
from scipy.interpolate import interp1d
import numpy as np


class TxtData:

    def __init__(self, filepath: str = None) -> None:
        if filepath is None:
            raise ValueError("Please provide a valid file name.")
        else:
            if not os.path.exists(filepath):
                raise FileNotFoundError("File not found.")
            else:
                if not filepath.endswith(".txt"):
                    raise ValueError("Please provide a valid file name. It has to be a .txt file.")
                else:
                    self.filepath = filepath
        self.data = self.load_data()

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath, sep=",")
        return df
