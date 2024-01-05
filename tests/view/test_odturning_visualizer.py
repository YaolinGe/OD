from unittest import TestCase
from src.view.ODTurningDataVisualizer import ODTurningDataVisualizer
from src.model.ODTurningData import ODTurningData


class TestODTurningVisualizer(TestCase):

        def setUp(self):
            filePath = "data/009_CoroPlus_231025-145417_00.xlsx"
            self.td = ODTurningData(filePath)
            self.tv = ODTurningDataVisualizer(self.td.df)
            pass

        def test_plot_od_turning(self):
            self.tv.plot_item()
            pass

