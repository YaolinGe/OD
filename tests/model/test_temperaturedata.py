"""
Unittest case for TemperatureData.py
"""

from unittest import TestCase
from src.model.TemperatureData import TemperatureData
import matplotlib.pyplot as plt


class TestTemperatureData(TestCase):

    def setUp(self):
        filePath = "data/temperature_85.csv"
        self.td = TemperatureData(filePath)

    def test_temperature_data(self):
        df = self.td.df
        df
