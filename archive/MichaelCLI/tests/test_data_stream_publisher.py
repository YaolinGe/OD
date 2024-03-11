from unittest import TestCase
from numpy import testing as npt
from src.DataStreamPublisher import DataStreamPublisher
import numpy as np
import os


class TestLiveViewer(TestCase):

    def setUp(self) -> None:
        self.dsp = DataStreamPublisher()

    def test_send_data(self) -> None:
        self.dsp.send_strain_gauge_ch0("1,2")
        self.dsp.send_strain_gauge_ch1("3,4")
        self.dsp.send_strain_gauge_ch2("5,6")
        self.dsp.send_strain_gauge_ch3("7,8")
        self.dsp.send_accelerometer("9,10,11,12")
