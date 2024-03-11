
#######################################################################################################################
#
#######################################################################################################################
from od_turning_error import OdTurningError

# import asyncio
import time


#######################################################################################################################
#
#######################################################################################################################
class MonitorService:

    ###################################################################################################################
    _status = 0x00000000

    SERVICE_UUID = "9049a6f7-a6d3-4624-a6ba-c2a2f81c5b01"
    STATUS_UUID = "9049a6f7-a6d3-4624-a6ba-c2a2f81c5b02"

    STATUS_OK = 0x00000000

    ###################################################################################################################
    def __init__(self, client):

        self._client = client

        return

    ###################################################################################################################
    def __enter__(self):

        return self

    ###################################################################################################################
    def __exit__(self, ex_type, ex_value, ex_traceback):

        return True

    ###################################################################################################################
    def service_available(self):

        for s in self._client.services:
            if MonitorService.SERVICE_UUID.casefold() == s.uuid.casefold():
                for c in s.characteristics:
                    if MonitorService.STATUS_UUID.casefold() == c.uuid.casefold():
                        return True

        return False

    ###################################################################################################################
    def sys_status_print(self):

        print("STATUS: {0}".format(self._status), flush=True)

    ###################################################################################################################
    async def sys_status_check_ok(self):

        if self._status == MonitorService.STATUS_OK:

            return True
        else:

            return False

    ###################################################################################################################
    async def sys_status_get(self):

        status = await self._client.read_gatt_char(self.STATUS_UUID)

        self._status = int.from_bytes(status, byteorder='little', signed=False)

        return self._status

    ###################################################################################################################
    def _callback_status_notification(self, uuid, data):

        print("Data received: {0}".format(data))

        self._status = int.from_bytes(data, byteorder='little', signed=False)

        print("STATUS: {0}".format(self._status))

        if self._status != MonitorService.STATUS_OK:
            self.sys_status_print()

    ###################################################################################################################
    async def notifications(self, enable):

        if enable:
            try: 
                print("Enabling notifications", flush=True)
                print("STATUS UUID: {0}".format(self.STATUS_UUID), flush=True)
                await self._client.start_notify(self.STATUS_UUID, self._callback_status_notification)
            except Exception as e:
                print("Error: {0}".format(e))
                raise OdTurningError("Error enabling notifications")

        else:

            await self._client.stop_notify(self.STATUS_UUID)
