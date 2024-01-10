"""
This class loads the cutFile and return a dataframe

Author: Yaolin Ge
Email: geyaolin@gmail.com
Date: 2024-01-10
"""
import clr
clr.AddReference(r"C:\Users\nq9093\CodeSpace\CSharp\Practice\DemoApp\CutFileReader\bin\Debug\net7.0\CutFileReader.dll")
from CutFileReader import CutFileLoader

CutFileLoader(r"C:\Users\nq9093\Downloads\ExportedFiles_20240105_024938\CoroPlus_230912-145816.cut")

# class CutFileLoader:
#
#     def __init__(self, filePath: str = None) -> None:
#         CutFileLoader(filePath)
#         pass


# if __name__ == "__main__":
#     cfl = CutFileLoader()