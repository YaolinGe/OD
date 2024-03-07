from unittest import TestCase
from numpy import testing as npt

from src.DataPool import DataPool

import numpy as np

import os

print(os.getcwd())


class TestLiveViewer(TestCase):

    def setUp(self) -> None:
        self.dp = DataPool()

    def test_live_streaming(self) -> None:

        pass

    def test_append_log_string_to_ch0(self) -> None:
        self.dp.append_strain_gauge_ch0("1.39404,8404465")
        self.dp.append_strain_gauge_ch0("1.40966,8404336")
        self.dp.append_strain_gauge_ch0("1.42528,8404463")

        npt.assert_array_equal(self.dp.strain_gauge_ch0, np.array([[1.39404, 8404465],
                                                                   [1.40966, 8404336],
                                                                   [1.42528, 8404463]]))

    def test_append_log_string_to_ch1(self) -> None:
        self.dp.append_strain_gauge_ch1("1.39404,8404465")
        self.dp.append_strain_gauge_ch1("1.40966,8404336")
        self.dp.append_strain_gauge_ch1("1.42528,8404463")

        npt.assert_array_equal(self.dp.strain_gauge_ch1, np.array([[1.39404, 8404465],
                                                                   [1.40966, 8404336],
                                                                   [1.42528, 8404463]]))

    def test_append_log_string_to_ch2(self) -> None:
        self.dp.append_strain_gauge_ch2("1.39404,8404465")
        self.dp.append_strain_gauge_ch2("1.40966,8404336")
        self.dp.append_strain_gauge_ch2("1.42528,8404463")

        npt.assert_array_equal(self.dp.strain_gauge_ch2, np.array([[1.39404, 8404465],
                                                                   [1.40966, 8404336],
                                                                   [1.42528, 8404463]]))

    def test_append_log_string_to_ch3(self) -> None:
        self.dp.append_strain_gauge_ch3("1.39404,8404465")
        self.dp.append_strain_gauge_ch3("1.40966,8404336")
        self.dp.append_strain_gauge_ch3("1.42528,8404463")

        npt.assert_array_equal(self.dp.strain_gauge_ch3, np.array([[1.39404, 8404465],
                                                                   [1.40966, 8404336],
                                                                   [1.42528, 8404463]]))

    def test_append_log_string_to_accelerometer(self) -> None:
        self.dp.append_accelerometer("1.29922,0.054600,-0.161304,0.991848")
        self.dp.append_accelerometer("1.29972,0.052104,-0.162474,0.996528")
        self.dp.append_accelerometer("1.30022,0.050076,-0.160446,0.996294")
        self.dp.append_accelerometer("1.30072,0.049374,-0.163176,0.992862")

        npt.assert_array_equal(self.dp.accelerometer, np.array([[1.29922, 0.054600, -0.161304, 0.991848],
                                                                     [1.29972, 0.052104, -0.162474, 0.996528],
                                                                     [1.30022, 0.050076, -0.160446, 0.996294],
                                                                     [1.30072, 0.049374, -0.163176, 0.992862]]))
