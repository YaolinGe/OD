"""
Unittest for the EDA class

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-24

"""

from unittest import TestCase
from src.EDA4Freq import EDA
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TestEDA(TestCase):

        def setUp(self):
            self.eda = EDA()

        def test_plot_data(self) -> None:
            self.eda.make_peak2peak_plot()
            # self.eda.make_plot_for_file()
            pass