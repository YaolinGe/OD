"""
Unittest for oddata.py
"""

from unittest import TestCase
from src.ExcelData import ExcelData
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TestExcelData(TestCase):

    def setUp(self):
        self.folderpath = os.path.join(os.getcwd(), "data")
        self.files = os.listdir(self.folderpath)
        self.filepath = os.path.join(self.folderpath, self.files[0])
        self.d = ExcelData(self.filepath)

    def test_load_data(self) -> None:
        # self.d.load_deflection_data()
        # self.d.load_data4rawdata()
        # self.d.load_data4temperature()
        # self.d.load_data4load()
        pass

    def test_synchorize_data(self) -> None:
        df = self.d.synchronize_data()
        pass
