"""
Unittest case for CutFileLoader.py
"""

from unittest import TestCase
from src.model.CutFileLoader import CutFileLoader
import matplotlib.pyplot as plt


class TestCutFileLoader(TestCase):

    def setUp(self):
        filePath = "C:\Users\nq9093\Downloads\ExportedFiles_20240105_024938\CoroPlus_230912-145816.cut"
        self.td = CutFileLoader(filePath)

    def test_odturning_data(self):
        df = self.td
        df
