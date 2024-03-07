
#######################################################################################################################
#
#######################################################################################################################
from od_turning_error import OdTurningError
from serial_port_service import SerialPortService
from teeness_protocol import TeenessProtocol, TeenessApplCmdPacket
from device_info_service import DeviceInfoService
from monitor_service import  MonitorService

# from bleak import discover
from bleak import BleakClient
from bleak import BleakScanner
# from bleak.exc import BleakDotNetTaskError
from bleak.exc import BleakError

import sys
import asyncio
import traceback
import optparse
import time
import msvcrt


#######################################################################################################################
#
#######################################################################################################################
class OdTurningBle:

    TEST_UUID = bytearray([0x6E, 0xE2, 0xD6, 0xF8, 0x10, 0x2A, 0x11, 0xEE, 0xBE, 0x56, 0x02, 0x42, 0xAC, 0x12, 0x00, 0x02])

    def __init__(self):

        self._parser = optparse.OptionParser(usage="%prog [options] (-h for help)\n")
        self._options = None
        self._settings = None
        self._argss = None

        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self.event_loop = asyncio.get_event_loop()
        self._client = None
        self._device_list = list()
        self._device_adv_list = list
        self._connected = False

        self.teeness_protocol = None
        self.serial_port_service = None
        self._device_info_service = None
        self.monitor_service = None

        self._UBLOX_MAC = list()
        self._UBLOX_MAC += ["CC:F9:57"]
        self._UBLOX_MAC += ["20:BA:36"]
        self._UBLOX_MAC += ["54:64:DE"]
        self._UBLOX_MAC += ["54:F8:2A"]
        self._UBLOX_MAC += ["60:09:C3"]
        self._UBLOX_MAC += ["6C:1D:EB"]
        self._UBLOX_MAC += ["D4:CA:6E"]

        self.LOG_PATH = r"..\..\Log"

    ###################################################################################################################
    def __enter__(self):

        self._default_args_init()

        # self._initialize()

        return self

    ###################################################################################################################
    def __exit__(self, ex_type, ex_value, ex_traceback):

        if ex_type is None and ex_value is None and ex_traceback is None:
            print("")
            print("EXIT_STS: SUCCESS")
        else:

            if self._connected:
                print("Disconnect emergency...")
                self.event_loop.run_until_complete(self._client.disconnect())

            if ex_type == OdTurningError:

                limit = None
            else:
                limit = None

            print("")
            print("***********************************************************")
            print("* EXIT MSG:")
            print("***********************************************************")
            print(traceback.print_exception(ex_type, ex_value, ex_traceback, limit))
            print("***********************************************************")
            print("")
            print("EXIT STS: ERROR")

        return True

    ####################################################################################################################
    def _default_args_init(self):

        # Execution control
        self._parser.set_defaults(loops=1)
        self._parser.add_option("-l", "--loops", dest="loops", type="int", help="Number of test loops")

        # Device
        # self._parser.set_defaults(address="CC:F9:57:9D:ED:FC")
        # self._parser.set_defaults(address="54:64:DE:2C:A4:C2")
        # self._parser.set_defaults(address="54:64:DE:2C:A4:CD")
        self._parser.set_defaults(address="54:64:DE:2C:A4:BF")
        self._parser.add_option("-u", "--uuid", dest="address", type="string", help="UUID used to scan/connect")

        self._options, self._argss = self._parser.parse_args()

    ###################################################################################################################
    async def _scan(self):

        print("Scanning for BLE devices...")

        self._device_list = list()
        device_dict = dict()

        device_dict.update(await BleakScanner.discover(return_adv=True))

        for d, a in device_dict.values():
            for u in self._UBLOX_MAC:
                if u.upper() in d.address.upper():
                    self._device_list.append((d, a))

        return self._device_list

    ###################################################################################################################
    async def scan_print_list(self):

        await self._scan()

        for i, d in enumerate(self._device_list):
            print("[{0:2d}]: {1} {2} {3} dBm".format(i, d[0].address, d[0].name, d[1].rssi))

    ###################################################################################################################
    async def scan_find(self):

        retry_counter = 1

        while retry_counter <= 5:

            await self._scan()

            for d in self._device_list:
                if d.address.upper().find(self._options.address.upper()) != -1:
                    print("Found: {0} {1}".format(d.address, d.name))
                    print("")

                    time.sleep(1)

                    return

            retry_counter += 1

        raise OdTurningError("OdTurningBle", "FAILED to find: {0}".format(self._options.address))

    ###################################################################################################################
    def connected(self):

        return self._connected

    ###################################################################################################################
    async def connect(self, device_list_pos=None, delay_after_connect_s=0.0):

        if device_list_pos is not None:
            self._options.address = self._device_list[device_list_pos][0].address

        loop = 0

        while loop < 5:

            loop += 1

            print("Connect attempt {0}...".format(loop))

            try:

                self._client = BleakClient(self._options.address, disconnected_callback=self.disconnect_callback,
                                           loop=self.event_loop)

                await asyncio.sleep(0.3)

                if await self._client.connect():

                    self.monitor_service = MonitorService(self._client)
                    self.serial_port_service = SerialPortService(self._client, self.event_loop)

                    retry = 5

                    while True:

                        if self.monitor_service.service_available() and self.serial_port_service.service_available():
                            break

                        if retry == 0:
                            raise OdTurningError("OdTurningBle", "FAILED to find Monitor service {0} or Serial Port Service {1}".format(
                                MonitorService.SERVICE_UUID, SerialPortService.SERIAL_PORT_SERVICE_UUID))

                        retry -= 1
                        await asyncio.sleep(0.5)

                    await asyncio.sleep(0.3)
                    await self.monitor_service.notifications(enable=True)
                    await self.serial_port_service.notifications(enable=True)

                    self.teeness_protocol = TeenessProtocol(self._client, self.event_loop, self.serial_port_service)

                    self._device_info_service = DeviceInfoService(self._client)

                    await asyncio.sleep(delay_after_connect_s)

                    self._connected = True

                    print("Connected to: {0}".format(self._client.address))
                    print("")

                    return

                else:
                    raise OdTurningError("OdTurningBle", "FAILED to connect to: {0}".format(self._options.address))

            except BleakError as b:

                if str(b).find("Connection to {0} was not successful!".format(self._options.address)) != -1:

                    # self.event_loop.run_until_complete(self._client.disconnect())
                    self._client = None
                    time.sleep(5)
                    continue
                else:

                    raise

        raise OdTurningError("OdTurningBle", "FAILED to connect to: {0}".format(self._options.address))

    ###################################################################################################################
    def disconnect_callback(self, client: BleakClient):

        self._connected = False

        print("DISCONNECTED event...", flush=True)

    ###################################################################################################################
    async def disconnect(self):

        print('Disconnecting...')

        await self.serial_port_service.notifications(enable=False)
        await self.monitor_service.notifications(enable=False)

        if await self._client.disconnect():

            while self._connected:
                await asyncio.sleep(0.1)

            self._device_info_service = None
            self.teeness_protocol = None
            self.serial_port_service = None
            self.monitor_service = None
            self._client = None

            await asyncio.sleep(0.5)

            print(f"Disconnected from ", self._options.address)

            #if sys.platform.find("win") >= 0:
            #    time.sleep(5)

        else:
            raise OdTurningError("OdTurningBle", "FAILED to disconnect from: {0}".format(self._client.address))

    ###################################################################################################################
    async def fw_disconnect(self, delay_before_disconnect_ms):

        print("FW Disconnecting...")

        await self.teeness_protocol.appl_cmd_fw_disconnect(delay_before_disconnect_ms=delay_before_disconnect_ms)

        while self._connected:
            await asyncio.sleep(0.1)

        if not await self._client.disconnect():
            raise OdTurningError("OdTurningBle", "FAILED to disconnect from: {0}".format(self._client.address))

        self._device_info_service = None
        self.teeness_protocol = None
        self.serial_port_service = None
        self.monitor_service = None
        self._client = None

        await asyncio.sleep(0.5)

        print(f"FW Disconnected from ", self._options.address)

    ###################################################################################################################

    async def pair(self, device_list_pos=None):

        print('Pairing...')

        if device_list_pos is not None:
            self._options.address = self._device_list[device_list_pos][0].address

        self._client = BleakClient(self._options.address, disconnected_callback=self.disconnect_callback,
                                   loop=self.event_loop)

        if await self._client.connect():

            self._connected = True

            print("")
            input("Press Enter when pairing is done!")
            print("")
            # await asyncio.sleep(10.0)

            if await self._client.disconnect():

                while self._connected:
                    await asyncio.sleep(0.1)

        print(f"Paired to ", self._options.address)

    ###################################################################################################################
    async def unpair(self):

        print('Unpairing...')

        await self._client.unpair()

        while self._connected:
            await asyncio.sleep(0.1)

        self._device_info_service = None
        self.teeness_protocol = None
        self.serial_port_service = None
        self.monitor_service = None
        self._client = None

        await asyncio.sleep(0.5)

        print(f"Unpaired from ", self._options.address)

    ###################################################################################################################
    async def restart(self, factory_reset=False, delay_before_reboot_ms=3000, delay_after_connect_s=0.0):

        print('Restarting...')

        start = time.time()

        await self.teeness_protocol.appl_cmd_reboot(factory_reset=factory_reset,
                                                    delay_before_reboot_ms=delay_before_reboot_ms)

        if factory_reset:

            await self.unpair()

            await asyncio.sleep(8.0)

        else:
            await self.disconnect()

            while (time.time() - (start + 2.0)) <= (delay_before_reboot_ms / 1000.0):
                await asyncio.sleep(0.10)

            await self.connect(delay_after_connect_s=delay_after_connect_s)

        print(f"Restarted ", self._options.address)

    ###################################################################################################################
    async def check_loop_exit(self):

        if msvcrt.kbhit() or not await self.monitor_service.sys_status_check_ok():

            status = await self.monitor_service.sys_status_get()

            print("STATUS: {0}".format(status))

            return True

        else:

            return False

    ###################################################################################################################
    async def connect_test(self):

            await self.scan_find()

            connect_loop = 0

            await self.connect(delay_after_connect_s=0.0)

            while not msvcrt.kbhit():

                connect_loop += 1

                # await self.connect(delay_after_connect_s=5.0)

                start_time = time.time()

                cmd_loop = 0
                while cmd_loop < 10:
                    cmd_loop += 1

                    print("")
                    print("PKT LOOP START: {0}".format(cmd_loop))

                    print("PC Address:        0x{0:04X}".format(
                        await self.teeness_protocol.address_request(OdTurningBle.TEST_UUID)))

                    self.teeness_protocol._dest_address = 3
                    self.teeness_protocol._source_address = 4

                    print("Connected Address: 0x{0:04X}".format(
                        await self.teeness_protocol.connected_devices_request()))

                    await self.teeness_protocol.appl_cmd_get_information()

                    await self.teeness_protocol.appl_cmd_get_version()

                    print("Device Type:       {0}".format(await self.teeness_protocol.appl_cmd_get_device_type()))

                    print("SYS CLOCK: {0} MHz".format(await self.teeness_protocol.appl_cmd_get_stream_sys_clock()))
                    await self.teeness_protocol.appl_cmd_set_stream_sys_clock(sys_clock_MHz=48)
                    print("SYS CLOCK: {0} MHz".format(await self.teeness_protocol.appl_cmd_get_stream_sys_clock()))
                    await self.teeness_protocol.appl_cmd_set_stream_sys_clock(sys_clock_MHz=12)
                    print("SYS CLOCK: {0} MHz".format(await self.teeness_protocol.appl_cmd_get_stream_sys_clock()))
                    await self.teeness_protocol.appl_cmd_set_stream_sys_clock(sys_clock_MHz=96)
                    print("SYS CLOCK: {0} MHz".format(await self.teeness_protocol.appl_cmd_get_stream_sys_clock()))

                    #print("STREAM START STS: {0}".format(await self.teeness_protocol.appl_cmd_stream_start(2, 4321)))
                    print("STREAM START STS: {0}".format(
                        await self.teeness_protocol.appl_cmd_stream_sbc2_strain_gauge_start(
                            sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_ALL,
                            analog_input_range=8080,
                            calib_output_rate_hz=1024,
                            data_output_rate_hz=100,
                            dac_offset_mV=0)))

                    await asyncio.sleep(10.0)

                    print("STREAM STOP STS:  {0}".format(await self.teeness_protocol.appl_cmd_stream_stop(
                        TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_ALL)))

                    print("PKT LOOP END: {0}".format(cmd_loop))

                end_time = time.time()

                # await ble.teeness_protocol.appl_cmd_reboot(delay_before_reboot_ms=4000)

                # await ble.disconnect()

                await self.restart(delay_before_reboot_ms=5000, delay_after_connect_s=0.0)

                total_time = end_time - start_time

                print("CONNECT LOOP TIME: {0:.3f} s/loop {1:.3f} s/cmd".format(
                    total_time, total_time / (14.0 * cmd_loop)))

                print("CONNECT LOOP END: {0}".format(connect_loop))

                await asyncio.sleep(2.0)

            await ble.disconnect()

            print("")


#######################################################################################################################
#
#######################################################################################################################
if __name__ == '__main__':

    try:
        with OdTurningBle() as ble:

            ble.event_loop.run_until_complete(ble.connect_test())

        exit(0)
    except:
        print("ERROR")
        exit(1)