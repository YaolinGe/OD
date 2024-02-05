#######################################################################################################################
#
#######################################################################################################################
# import time
# import asyncio
import asyncio
import threading
import time


#######################################################################################################################
#
#######################################################################################################################
class SerialPortService:

    ###################################################################################################################
    SERIAL_PORT_SERVICE_UUID = "2456E1B9-26E2-8F83-E744-F34F01E9D701"
    SERIAL_PORT_FIFO_CHAR_UUID = "2456E1B9-26E2-8F83-E744-F34F01E9D703"

    ###################################################################################################################
    def __init__(self, client, event_loop):

        self._client = client
        self._event_loop = event_loop

        self._data = bytearray()

        self._lock = threading.Lock()

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
            if SerialPortService.SERIAL_PORT_SERVICE_UUID.casefold() == s.uuid.casefold():
                for c in s.characteristics:
                    if SerialPortService.SERIAL_PORT_FIFO_CHAR_UUID.casefold() == c.uuid.casefold():
                        return True

        return False
    ###################################################################################################################
    async def send(self, buffer):

        await self._client.write_gatt_char(self.SERIAL_PORT_FIFO_CHAR_UUID, buffer)

        #self._event_loop.run_until_complete(
        #    self._client.write_gatt_char(self.SERIAL_PORT_FIFO_CHAR_UUID, buffer))

    ###################################################################################################################
    """
    def receive(self, data_length=1024, timeout_s=0.0):

        timeout = time.time() + timeout_s

        while (len(self._data) == 0) and (time.time() <= timeout):
            self._event_loop.run_until_complete(asyncio.sleep(0.01))

        if data_length > len(self._data):
            data_length = len(self._data)

        tmp_data = self._data[0:data_length]

        self._data = self._data[data_length:]

        return tmp_data
    """

    async def receive(self, data_length=1024):

        tmp_data = bytearray()

        self._lock.acquire()

        if len(self._data) > 0:

            if data_length > len(self._data):
                data_length = len(self._data)

            tmp_data = self._data[0:data_length]

            self._data = self._data[data_length:]

        self._lock.release()

        return tmp_data

    ###################################################################################################################
    async def clear(self):
        self._data = bytearray()

    ###################################################################################################################
    async def received_bytes(self):
        self._lock.acquire()

        no_of_bytes = len(self._data)

        self._lock.release()

    ###################################################################################################################
    def _callback_data_received_notification(self, uuid, data):

        """
        print("Length: {0}".format(len(data)))
        for d in data:
            print("{:02X} ".format(d), end='')
        print("")
        """

        self._lock.acquire()

        self._data.extend(data)

        self._lock.release()

        return

    ###################################################################################################################
    async def notifications(self, enable):

        if enable:

            await self._client.start_notify(self.SERIAL_PORT_FIFO_CHAR_UUID, self._callback_data_received_notification)

        else:

            await self._client.stop_notify(self.SERIAL_PORT_FIFO_CHAR_UUID)
