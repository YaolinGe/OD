from unittest import TestCase
from numpy import testing as npt
from src.DataStreamSubscriber import DataStreamSubscriber



class TestLiveViewer(TestCase):

    def setUp(self) -> None:
        self.dss = DataStreamSubscriber()

    def test_live_streaming(self) -> None:
        self.dss.start_subscriber()
