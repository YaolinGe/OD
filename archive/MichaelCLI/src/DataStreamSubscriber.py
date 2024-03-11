import numpy as np
import asyncio
import websockets
import threading


class DataStreamSubscriber:
    def __init__(self):
        self.data_arrays = {
            "strain_gauge_ch0": np.empty([0, 2]),
            "strain_gauge_ch1": np.empty([0, 2]),
            "strain_gauge_ch2": np.empty([0, 2]),
            "strain_gauge_ch3": np.empty([0, 2]),
            "accelerometer_raw": np.empty([0, 4]),
            "accelerometer_mG": np.empty([0, 4]),
        }
        self.MAX_DATA_POINTS = 5000

    async def handle_websocket(self, websocket, path):
        try:
            while True:
                message = await websocket.recv()
                # print(f"Received message: {message}")
                self.parse_message(message)
        except websockets.ConnectionClosed:
            pass

    def parse_message(self, message: str) -> None:
        message_mapping = {
            "strain_gauge_ch0: ": "strain_gauge_ch0",
            "strain_gauge_ch1: ": "strain_gauge_ch1",
            "strain_gauge_ch2: ": "strain_gauge_ch2",
            "strain_gauge_ch3: ": "strain_gauge_ch3",
            "accelerometer_raw: ": "accelerometer_raw",
            "accelerometer_mG: ": "accelerometer_mG",
        }

        for key, value in message_mapping.items():
            if message.startswith(key):
                data = np.array([float(i) for i in message.split(": ")[1].split(",")]).reshape(1, -1)
                self.data_arrays[value] = np.append(self.data_arrays[value], data, axis=0)
                if self.data_arrays[value].shape[0] > self.MAX_DATA_POINTS:
                    self.data_arrays[value] = self.data_arrays[value][1:]
                break
        else:
            print(f"Ignored message: {message}")

    def start_subscriber_thread(self):
        def run():
            asyncio.set_event_loop(asyncio.new_event_loop())  # Set a new event loop for the thread
            start_server = websockets.serve(self.handle_websocket, "localhost", 8765)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()

        thread = threading.Thread(target=run)
        thread.start()
        print("WebSocket server running localhost:8765...")


if __name__ == "__main__":
    subscriber = DataStreamSubscriber()
    # subscriber.start_subscriber()
