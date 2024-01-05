"""
Unittest case for ODTurningData.py
"""

from unittest import TestCase
from src.model.ODTurningData import ODTurningData
import matplotlib.pyplot as plt


class TestODTurningData(TestCase):

    def setUp(self):
        filePath = "data/009_CoroPlus_231025-145417_00.xlsx"
        self.td = ODTurningData(filePath).df

    def test_odturning_data(self):
        df = self.td
        df
