"""
Singleton class for TemperatureData

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-16
"""
from model.TemperatureData import TemperatureData


class SingletonTemperatureData:
    _instances = {}

    @classmethod
    def get_instance(cls, filename):
        if filename not in cls._instances:
            cls._instances[filename] = TemperatureData(filename)
        return cls._instances[filename]


if __name__ == "__main__":
    filename = "data/temperature_85.csv"

    from time import time
    t1 = time()
    td = SingletonTemperatureData.get_instance(filename)
    t2 = time()
    print(t2 - t1)

    t1 = time()
    td = SingletonTemperatureData.get_instance(filename)
    t2 = time()
    print(t2 - t1)

    filename = "data/temperature_37.csv"
    t1 = time()
    td = SingletonTemperatureData.get_instance(filename)
    t2 = time()
    print(t2 - t1)

    t1 = time()
    td = SingletonTemperatureData.get_instance(filename)
    t2 = time()
    print(t2 - t1)

    # print(td.df)

