from unittest import TestCase
from src.view.TemperatureVisualizer import TemperatureVisualizer
from src.model.TemperatureData import TemperatureData


class TestTemperatureVisualizer(TestCase):

        def setUp(self):
            filePath = "data/temperature_85.csv"
            self.td = TemperatureData(filePath)
            self.tv = TemperatureVisualizer(self.td.df)
            pass

        def test_plot_temperature(self):
            self.tv.plot_temperature()
            pass


