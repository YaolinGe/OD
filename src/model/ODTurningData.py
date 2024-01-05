"""
OD Turning data class to handle OD Turning data.

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01--05
"""
from ExcelData import ExcelData
import os
import pandas as pd
import numpy as np


def validate_file(filepath):
    if filepath is None:
        raise ValueError("Please provide a valid file name.")
    if not os.path.exists(filepath):
        raise FileNotFoundError("File not found.")
    if not filepath.endswith(".xlsx"):
        raise ValueError("Please provide a valid excel spreadsheet file.")
    if not os.path.getsize(filepath) > 0:
        raise ValueError("The file is empty.")


class ODTurningData:
    def __init__(self, filepath: str = None) -> None:
        validate_file(filepath)
        self.filepath = filepath
        self.load_data()

    def load_data(self) -> None:
        self.df = ExcelData(self.filepath).df_sync  # Read file once


if __name__ == "__main__":
    td = ODTurningData()



