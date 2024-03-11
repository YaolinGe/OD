"""
DataStreamPublisher will handle the data streaming to the WebSocket server.
The data will be published to the server using the WebSocket protocol.
"""
import asyncio
import websockets
import numpy as np


class DataStreamPublisher:

    def __init__(self) -> None:
        # s0, set up the connection with the server
        self.uri = "ws://localhost:8765"
        print(f"Connecting to {self.uri}...")
        # self.counter = 0

    def run_test(self) -> None: 
        def generate_strain_gauge_data(self) -> np.ndarray:
            """ Generate sine wave data with normal noise, 1 sec duration, 100 Hz sampling rate """
            t = np.arange(0, 1, 0.01)
            data = np.sin(2 * np.pi * 10 * t) + np.random.normal(0, 0.1, len(t))
            return np.array([t, data]).T

        def generate_acc_data(self) -> np.ndarray:
            """ Generate sine wave data with white noise, 1 sec duration, 100 Hz sampling rate, but for x, y, z, x, y, z should have different sine waves """
            t = np.arange(0, 1, 0.01)
            data = np.sin(2 * np.pi * 10 * t) + np.random.normal(0, 0.1, len(t))
            return np.array([t, data, data, data]).T

        # s1, generate the simulated data
        self.strain_gauge_ch0 = self.generate_strain_gauge_data()
        self.strain_gauge_ch1 = self.generate_strain_gauge_data()
        self.strain_gauge_ch2 = self.generate_strain_gauge_data()
        self.strain_gauge_ch3 = self.generate_strain_gauge_data()
        self.accelerometer_raw = self.generate_acc_data()
        print("Data generated...")

        # s2, loop through the data such as strain_gauge_ch0, strain_gauge_ch1, strain_gauge_ch2, strain_gauge_ch3, accelerometer_raw and convert each data to string and send it to the server
        loop = asyncio.get_event_loop()
        for i in range(len(self.strain_gauge_ch0)):
            loop.run_until_complete(self.send_strain_gauge_ch0("{0},{1}".format(self.strain_gauge_ch0[i][0], self.strain_gauge_ch0[i][1])))
            loop.run_until_complete(self.send_strain_gauge_ch1("{0},{1}".format(self.strain_gauge_ch1[i][0], self.strain_gauge_ch1[i][1])))
            loop.run_until_complete(self.send_strain_gauge_ch2("{0},{1}".format(self.strain_gauge_ch2[i][0], self.strain_gauge_ch2[i][1])))
            loop.run_until_complete(self.send_strain_gauge_ch3("{0},{1}".format(self.strain_gauge_ch3[i][0], self.strain_gauge_ch3[i][1])))
            loop.run_until_complete(self.send_accelerometer_raw("{0},{1},{2},{3}".format(self.accelerometer_raw[i][0], self.accelerometer_raw[i][1], self.accelerometer_raw[i][2], self.accelerometer_raw[i][3])))

    async def send_strain_gauge_ch0(self, log_string: str):
        await self.send_data("strain_gauge_ch0: " + log_string)

    async def send_strain_gauge_ch1(self, log_string: str):
        await self.send_data("strain_gauge_ch1: " + log_string)

    async def send_strain_gauge_ch2(self, log_string: str):
        await self.send_data("strain_gauge_ch2: " + log_string)

    async def send_strain_gauge_ch3(self, log_string: str):
        await self.send_data("strain_gauge_ch3: " + log_string)

    async def send_accelerometer_raw(self, log_string: str):
        pass
        # await self.send_data("accelerometer_raw: " + log_string)

    async def send_accelerometer_mG(self, log_string: str):
        await self.send_data("accelerometer_mG: " + log_string)

    async def send_data(self, data_string: str):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(data_string)
            # self.counter += 1
            # if self.counter % 1000 == 0:
            #     print(f"Sent message: {data_string}")
            # print(f"Sent message: {data_string}")


if __name__ == "__main__":
    publisher = DataStreamPublisher()

