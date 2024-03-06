import time
import numpy as np
import datetime
import os
import asyncio

start_time = time.time()
log_folder = 'C:\\Log'
channels = ["CH{:s}".format(ch) for ch in "0123"]
timestring = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
files = [os.path.join(log_folder, "SG-BT-{:s}-V2-Dataset-{:s}.txt".format(ch, timestring)) for ch in channels]
file_acc = os.path.join(log_folder, "ACC-Dataset-{:s}.txt".format(timestring))



def clean_data():
    for file in files:
        with open(file, "w") as f:
            f.write("Timestamp_S,Data\n")
    with open(file_acc, "w") as f:
        f.write("Timestamp_S,X,Y,Z\n")
    print("Data cleaned")


def generate_random_data():
    """ Generate a random array with index 0 with current timestamp, and index 1 with a random number but this random
     number changes with time as a sine wave. """
    timestamp = time.time() - start_time
    return np.array([timestamp, np.sin(timestamp * 2 * np.pi * 0.1) + np.random.normal(0, 0.5)])


def generate_random_acc_data():
    """ Generate a random array with index 0 with current timestamp, and index 1 with a random number but this random
     number changes with time as a sine wave. """
    timestamp = time.time() - start_time
    return np.array([timestamp,
                     np.sin(timestamp * 2 * np.pi * 0.1) + np.random.normal(0, 0.5),
                     np.sin(timestamp * 2 * np.pi * 0.2) + np.random.normal(0, 0.5),
                     np.sin(timestamp * 2 * np.pi * 0.3) + np.random.normal(0, 0.5)])


async def simulate_streaming():
    """ Simulate a data stream from a sensor from IOT bluetooth connected device, periodically saves data to a file,
    and print out the data to the console """
    t1 = time.time()
    t2 = t1
    clean_data()
    while True and (t2 - t1) < 300:  # Simulate 1 minute of data streaming
        await asyncio.sleep(1/12)  # 12 Hz
        for file in files:
            data = generate_random_data()
            with open(file, "a") as f:
                f.write("{:.2f},{:.2f}\n".format(data[0], data[1]))

        data = generate_random_acc_data()
        with open(file_acc, "a") as f:
            f.write("{:.2f},{:.2f},{:.2f},{:.2f}\n".format(data[0], data[1], data[2], data[3]))

        t2 = time.time()

if __name__ == "__main__":
    asyncio.run(simulate_streaming())

