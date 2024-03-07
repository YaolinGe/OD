"""
This data pool is used to store the data from the BLE device, and then it is used by the LiveViewer to display the
live view of the streaming data from the BLE device.
"""
import numpy as np
import websockets
import asyncio


class DataPool:

    def __init__(self) -> None:
        self.strain_gauge_ch0 = np.empty([0, 2])
        self.strain_gauge_ch1 = np.empty([0, 2])
        self.strain_gauge_ch2 = np.empty([0, 2])
        self.strain_gauge_ch3 = np.empty([0, 2])
        self.accelerometer = np.empty([0, 4])

        asyncio.get_event_loop().run_until_complete(self.run_websocket_server())

    def append_strain_gauge_ch0(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch0 = np.append(self.strain_gauge_ch0, data_sg, axis=0)

    def append_strain_gauge_ch1(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch1 = np.append(self.strain_gauge_ch1, data_sg, axis=0)

    def append_strain_gauge_ch2(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch2 = np.append(self.strain_gauge_ch2, data_sg, axis=0)

    def append_strain_gauge_ch3(self, log_string: str):
        data_sg = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.strain_gauge_ch3 = np.append(self.strain_gauge_ch3, data_sg, axis=0)

    def append_accelerometer(self, log_string: str):
        data_acc = np.array([float(i) for i in log_string.split(",")]).reshape(1, -1)
        self.accelerometer = np.append(self.accelerometer, data_acc, axis=0)

    async def send_data(self, websocket, path):
        # Here, you would manage sending data to the connected websocket client.
        # The implementation depends on how you wish to stream the data.
        while True:
            # Example: Send the latest accelerometer data periodically
            if len(self.accelerometer) > 0:
                await websocket.send(str(self.accelerometer[-1]))
            await asyncio.sleep(1)  # Sleep for a bit before sending the next update

    async def run_websocket_server(self):
        start_server = websockets.serve(self.send_data, "localhost", 8765)
        await start_server


async def main():
    dp = DataPool()
    await dp.run_websocket_server()


if __name__ == "__main__":
    asyncio.run(main())

