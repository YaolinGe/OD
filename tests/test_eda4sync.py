"""
Unittest for the EDA class

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2023-11-24

"""

from unittest import TestCase
from src.EDA4Sync import EDA
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TestEDA(TestCase):

        def setUp(self):
            self.eda = EDA()

        def test_plot_data(self) -> None:
            self.eda.make_plots_for_all_files()
            pass