import asyncio
from bleak import BleakScanner, BleakClient


async def scan_devices():
    device_dict = dict()
    device_dict.update(await BleakScanner.discover(return_adv=True))
    return device_dict


async def connect_and_disconnect(ublox_mac: list[str]):
    device_dict = await scan_devices()
    device_list = []

    for d, a in device_dict.values():
        for u in ublox_mac:
            if u.upper() in d.address.upper():
                device_list.append((d, a))

    # print name and address and rssi of all devices
    for d, a in device_list:
        print(f"{d.name} ({d.address}) : {a.rssi}")

    # Attempt to connect to the first device in the list
    if device_list:
        device = device_list[0][0]  # Get the first device and its advertisement data
        async with BleakClient(device.address) as client:
            connected = await client.connect()
            print(f"Connected to {device.address}: {connected}")
            await client.read_gatt_char("9049a6f7-a6d3-4624-a6ba-c2a2f81c5b02")
        print(f"Disconnected from {device.address}")
    else:
        print("No target devices found.")

UBLOX_MAC = [
    "CC:F9:57",
    "20:BA:36",
    "54:64:DE",
    "54:F8:2A",
    "60:09:C3",
    "6C:1D:EB",
    "D4:CA:6E",
]


if __name__ == "__main__":
    asyncio.run(connect_and_disconnect(UBLOX_MAC))
