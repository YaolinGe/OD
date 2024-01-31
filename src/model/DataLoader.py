"""
Baseclass for all data loaders

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-29
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class DataLoader:

    def __init__(self, dataScheme: DataScheme, filePath: str) -> None:
        self._dataScheme = dataScheme
        # I need to think about how I can specify the data file path
        pass

    @property
    def dataScheme(self) -> DataScheme:
        return self._dataScheme

    @dataScheme.setter
    def dataScheme(self, dataScheme: DataScheme) -> None:
        self._dataScheme = dataScheme

    def execute(self) -> None:
        self.dataScheme.load_data()
        pass


class DataScheme(ABC):

    @abstractmethod
    def load_data(self) -> None:
        pass
    pass

class TemperatureDataScheme(DataScheme):

    def load_data(self) -> None:
        print("Load temperature data")
        pass
    pass

class CutFileDataScheme(DataScheme):
    def load_data(self) -> None:
        print("Load cut file data")
        pass
    pass


if __name__ == "__main__":
    dl_temp = DataLoader(TemperatureDataScheme(), "data/temperature_85.csv")
    dl_temp.execute()

    dl_temp.dataScheme = CutFileDataScheme()
    dl_temp.execute()
    pass
