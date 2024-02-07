
#######################################################################################################################
#
#######################################################################################################################
from bleak.uuids import uuid16_dict

import sys
# import asyncio


#######################################################################################################################
#
#######################################################################################################################
class DeviceInfoService:

    ###################################################################################################################
    def __init__(self, client):

        self._device_name = None
        self._manufacturer_name = None
        self._model_number = None
        self._serial_number = None
        self._hw_revision = None
        self._fw_revision = None
        self._sw_revision = None

        self._uuid16_dict = {v: k for k, v in uuid16_dict.items()}

        self.MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Manufacturer Name String"))

        self.MODEL_NUM_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Model Number String"))

        self.SERIAL_NUM_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Serial Number String"))

        self.HARDWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Hardware Revision String"))

        self.FIRMWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Firmware Revision String"))

        self.SOFTWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Software Revision String"))

        self.SYSTEM_ID_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("System ID"))

        self.DEVICE_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            self._uuid16_dict.get("Device Name"))

        self._client = client

    ###################################################################################################################
    def __enter__(self):

        return self

    ###################################################################################################################
    def __exit__(self, ex_type, ex_value, ex_traceback):

        return True

    ###################################################################################################################
    async def _read_string(self, uuid, print_it, header):

        response = await self._client.read_gatt_char(uuid)

        response = str(response.decode('utf-8'))

        if print_it:
            print("* {0} {1}".format(header, response))

        return response

    ###################################################################################################################
    async def device_info_get(self, print_it=True):

        if print_it:
            print("********************* Device Info *********************")

        if sys.platform.find("win") >= 0:
            self._device_name = await self._read_string(self.DEVICE_NAME_UUID, print_it, "Device name:       ")

        self._manufacturer_name = await self._read_string(self.MANUFACTURER_NAME_UUID, print_it, "Manufacturer name: ")

        self._model_number = await self._read_string(self.MODEL_NUM_UUID, print_it, "Model number:      ")

        self._serial_number = await self._read_string(self.SERIAL_NUM_UUID, print_it, "Serial number:     ")

        self._hw_revision = await self._read_string(self.HARDWARE_REV_UUID, print_it, "Hardware revision: ")

        self._fw_revision = await self._read_string(self.FIRMWARE_REV_UUID, print_it, "Firmware revision: ")

        self._sw_revision = await self._read_string(self.SOFTWARE_REV_UUID, print_it, "Software revision: ")

        if print_it:
            print("*")
            print("*******************************************************")

    ###################################################################################################################
    async def device_info_model_get(self, print_it=True):

        if print_it:
            print("********************* Device Info *********************")

        self._model_number = await self._read_string(self.MODEL_NUM_UUID, print_it, "Model number:      ")

        if print_it:
            print("*")
            print("*******************************************************")

        return self._model_number
