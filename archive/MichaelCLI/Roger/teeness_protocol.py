#######################################################################################################################
#
#######################################################################################################################
from od_turning_error import OdTurningError
import asyncio
import binascii
import threading
# import time


#######################################################################################################################
#
#######################################################################################################################
class TeenessPacket:

    ADDRESS_REQUEST = 1
    ADDRESS_RESPONSE = 2
    DEVICE_INFORMATION_REQUEST = 4
    DEVICE_INFORMATION_RESPONSE = 5
    CONNECTED_DEVICES_REQUEST = 10
    CONNECTED_DEVICES_RESPONSE = 11

    APPLICATION = 8

    def __init__(self):
        self.data_length = 0
        self.packet_counter = 0
        self.source_address = 0
        self.dest_address = 0
        self.packet_type = 0
        self.data_bytes = None
        self.crc = 0
        self.calc_crc = 0


#######################################################################################################################
#
#######################################################################################################################
class TeenessApplCmdPacket:

    START_STREAM = 1
    STOP_STREAM = 3
    DATA_STREAM = 9
    CMD_REPLY = 100
    GET_INFORMATION2 = 107
    GET_DEVTYPE = 116
    GET_VERSION = 122
    REBOOT = 123

    GET_BLE_CONNECTION_STS = 132
    SET_BLE_FW_DISCONNECT = 133
    SET_BLE_STREAM_OUTPUT_STATE = 134
    SET_SYS_DEEP_POWER_DOWN = 135

    STREAM_SENSOR_ID_NONE = 0
    STREAM_SENSOR_ID_SG_BT1 = 11
    STREAM_SENSOR_ID_SG_BT2 = 12
    STREAM_SENSOR_ID_SG_BT1_BT2 = 13
    STREAM_SENSOR_ID_MCU_HUMIDITY = 21
    STREAM_SENSOR_ID_SBC1_ACCEL_mG = 31
    STREAM_SENSOR_ID_SBC1_ACCEL_RAW = 32
    STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE = 39
    STREAM_SENSOR_ID_SG_V2_BT = 41

    STREAM_SENSOR_SG_ANALOG_INPUT_RANGE_m10_p10_mV = 1010
    STREAM_SENSOR_SG_ANALOG_INPUT_RANGE_m20_p20_mV = 2020
    STREAM_SENSOR_SG_ANALOG_INPUT_RANGE_m40_p40_mV = 4040
    STREAM_SENSOR_SG_ANALOG_INPUT_RANGE_m80_p80_mV = 8080

    def __init__(self, cmd, request_id, expected_data_length, teeness_packet):

        if cmd != teeness_packet.data_bytes[1]:
            print("#######################################")
            print("Length: {0}".format(len(teeness_packet.data_bytes)))
            for d in teeness_packet.data_bytes:
                print("{:02X} ".format(d), end='')
            print("")
            print("#######################################")
            raise OdTurningError("TeenessApplCmdPacket", "Invalid command id. Expected {0}. Received {1}".format(cmd, teeness_packet.data_bytes[1]))

        if self.CMD_REPLY != teeness_packet.data_bytes[0]:
            raise OdTurningError("TeenessApplCmdPacket", "Invalid response indicator. Expected {0}. Received {1}".format(self.CMD_REPLY, teeness_packet.data_bytes[0]))

        req_id = int.from_bytes(teeness_packet.data_bytes[teeness_packet.data_length - 2:],
                                byteorder="little", signed=False)
        if request_id != req_id:
            raise OdTurningError("TeenessApplCmdPacket", "Invalid request id")

        self.data_bytes = teeness_packet.data_bytes[2:teeness_packet.data_length - 2]

        if expected_data_length != len(self.data_bytes):
            raise OdTurningError("TeenessApplCmdPacket", "Invalid data_length. Expected {0} got {1}".format(
                expected_data_length, len(self.data_bytes)))


#######################################################################################################################
#
#######################################################################################################################
class TeenessProtocol:

    ###################################################################################################################
    def __init__(self, client, event_loop, serial_port_service):

        self._client = client
        self._event_loop = event_loop
        self._serial_port_service = serial_port_service
        self._source_address = 0xFFFF
        self._dest_address = 0xFFFF

        self._packet_counter_outbound = 0
        self._appl_cmd_request_id_outbound = 0

        self._data = bytearray()
        self._crc_error_counter = 0

        self._bt_v2_packets = 0
        self._bt1_packets = 0
        self._bt2_packets = 0
        self._humidity_packets = 0
        self._accel_temperature_packets = 0
        self._accel_packets = 0

        return

    ###################################################################################################################
    def crc_error_counter_get(self):

        return self._crc_error_counter

    ###################################################################################################################
    async def _receive_data(self, no_of_bytes):

        data = await self._serial_port_service.receive(no_of_bytes)

        while len(data) < no_of_bytes:

            await asyncio.sleep(0.001)

            data += await self._serial_port_service.receive(no_of_bytes - len(data))

        return data

    ###################################################################################################################
    async def _start_pattern_wait(self):

        while True:

            byte = await self._receive_data(1)
            if (len(byte) == 1) and (byte[0] == 0x00):
                byte = await self._receive_data(1)
                if (len(byte) == 1) and (byte[0] == 0xFF):
                    byte = await self._receive_data(1)
                    if (len(byte) == 1) and (byte[0] == 0x00):
                        byte = await self._receive_data(1)
                        if (len(byte) == 1) and (byte[0] == 0xFF):
                            break
        return

    ###################################################################################################################
    async def _header_wait(self):

        packet = TeenessPacket()

        header_bytes = await self._receive_data(11)

        # header_bytes = await self._serial_port_service.receive(11)

        # while len(header_bytes) < 11:
        #    header_bytes += await self._serial_port_service.receive(11 - len(header_bytes))

        packet.data_length = int.from_bytes(header_bytes[0:2], byteorder ="little", signed=False)
        packet.packet_counter = int.from_bytes(header_bytes[2:4], byteorder ="little", signed=False)
        packet.source_address = int.from_bytes(header_bytes[4:6], byteorder ="little", signed=False)
        packet.dest_address = int.from_bytes(header_bytes[6:8], byteorder ="little", signed=False)
        packet.packet_type = int.from_bytes(header_bytes[8:9], byteorder ="little", signed=False)
        packet.crc = int.from_bytes(header_bytes[9:11], byteorder="little", signed=False)

        packet.calc_crc = binascii.crc_hqx(header_bytes[0:9], 0xFFFF)

        return packet

    ###################################################################################################################
    async def _data_wait(self, packet):

        packet.data_bytes = await self._receive_data(packet.data_length)

        # header.data_bytes = await self._serial_port_service.receive(header.data_length)

        # while len(header.data_bytes) < header.data_length:
        #    header.data_bytes += await self._serial_port_service.receive(header.data_length - len(header.data_bytes))

        packet.calc_crc = binascii.crc_hqx(packet.data_bytes, packet.calc_crc)

        # return data_bytes

    ###################################################################################################################
    async def   receive_packet(self, debug=False):

        while True:

            await self._start_pattern_wait()

            packet = await self._header_wait()

            await self._data_wait(packet)

            #print("DATA: {0} {1} {2} {3} {4} {5}".format(header.data_length, header.packet_counter, header.source_address,
            #                                             header.dest_address, header.packet_type, header.data_bytes))
            # print("CRC: {0:04X} {1:04X}".format(packet.calc_crc, packet.crc))

            if debug:
                print("L: {0}".format(packet.data_length))
                print("R: ", end='')
                for p in packet.data_bytes:
                    print("{0:02X}".format(p), end='')
                print("")

            if packet.calc_crc != packet.crc:
                print("L: {0}".format(packet.data_length))
                print("R: ", end='')
                for p in packet.data_bytes:
                    print("{0:02X}".format(p), end='')
                print("")
                self._crc_error_counter += 1
                continue

                # raise OdTurningError("TeenessProtocol", "CRC error in Teeness package")
            # else:
                #    print("Packet OK (0x{0:02X})!!!".format(packet.crc))
            break

        return packet

    ###################################################################################################################
    async def send_packet(self, source_address, dest_address, packet_type, data):

        packet = bytearray([0x00, 0xFF, 0x00, 0xFF])

        self._packet_counter_outbound = 3

        packet.extend(len(data).to_bytes(2, byteorder='little', signed=False))
        packet.extend((int(self._packet_counter_outbound).to_bytes(2, byteorder='little', signed=False)))
        packet.extend((int(source_address).to_bytes(2, byteorder='little', signed=False)))
        packet.extend((int(dest_address).to_bytes(2, byteorder='little', signed=False)))
        packet.extend((int(packet_type).to_bytes(1, byteorder='little', signed=False)))

        calc_crc = binascii.crc_hqx(packet[4:], 0xFFFF)
        calc_crc = binascii.crc_hqx(data, calc_crc)

        packet.extend((int(calc_crc).to_bytes(2, byteorder='little', signed=False)))

        packet.extend(data)

        """
        print("S: ", end='')
        for p in packet:
            print("{0:02X}".format(p), end='')
        print("")
        """

        await self._serial_port_service.send(packet)

        self._packet_counter_outbound += 1

    ###################################################################################################################
    async def address_request(self, uuid):

        await self.send_packet(source_address=0xFFFF, dest_address=0xFFFF,
                               packet_type=TeenessPacket.ADDRESS_REQUEST,
                               data=uuid)

        packet = await self.receive_packet()

        if packet.packet_type != TeenessPacket.ADDRESS_RESPONSE:
            raise OdTurningError("TeenessProtocol", "Invalid packet type {0}. Expected {1}".format(
                packet.packet_type, TeenessPacket.ADDRESS_RESPONSE))

        if uuid != packet.data_bytes[0:packet.data_length - 2]:
            raise OdTurningError("TeenessProtocol", "Invalid UUID returned {0}".format(
                packet.data_bytes[0:packet.data_length - 2]))

        self._source_address = int.from_bytes(packet.data_bytes[packet.data_length - 2:], byteorder='little', signed=False)

        return self._source_address

    ###################################################################################################################
    async def connected_devices_request(self):

        await self.send_packet(source_address=self._source_address, dest_address=0xFFFF,
                               packet_type=TeenessPacket.CONNECTED_DEVICES_REQUEST,
                               data=bytearray())

        packet = await self.receive_packet()

        if packet.packet_type != TeenessPacket.CONNECTED_DEVICES_RESPONSE:
            raise OdTurningError("TeenessProtocol", "Invalid packet type {0}. Expected {1}".format(
                packet.packet_type, TeenessPacket.CONNECTED_DEVICES_RESPONSE))

        self._dest_address = packet.source_address

        return self._dest_address

    ###################################################################################################################
    async def send_appl_cmd(self, cmd, data):

        send_data = bytearray()
        send_data.extend(int(cmd).to_bytes(1, byteorder='little', signed=False))
        # send_data.extend(int(self._appl_cmd_request_id_outbound).to_bytes(2, byteorder='little', signed=False))
        send_data.extend(data)

        self._appl_cmd_request_id_outbound = 3
        send_data.extend(int(self._appl_cmd_request_id_outbound).to_bytes(2, byteorder='little', signed=False))

        await self.send_packet(source_address=self._source_address, dest_address=self._dest_address,
                               packet_type=TeenessPacket.APPLICATION,
                               data=send_data)

    ###################################################################################################################
    async def exec_appl_cmd(self, cmd, data, expected_response_length):

        await self.send_appl_cmd(cmd, data)

        appl_cmd_packet = TeenessApplCmdPacket(cmd, self._appl_cmd_request_id_outbound,
                                               expected_response_length, await self.receive_packet())

        self._appl_cmd_request_id_outbound += 1

        return appl_cmd_packet

    ###################################################################################################################
    async def appl_cmd_get_information(self):

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.GET_INFORMATION2, bytearray(), 41)

        uuid = appl_cmd_packet.data_bytes[0:16]
        build_date = appl_cmd_packet.data_bytes[22:33].decode('utf-8')
        build_time = appl_cmd_packet.data_bytes[33:].decode('utf-8')

        """
        print("UUID:       ", end='')
        for b in appl_cmd_packet.data_bytes[0:16]:
            print("{0:02X}".format(b), end='')
        print("")

        # print("Build date: {0}".format(appl_cmd_packet.data_bytes[22:].decode('utf-8')))
        print("Build date: {0}".format(appl_cmd_packet.data_bytes[22:33].decode('utf-8')))
        print("Build time: {0}".format(appl_cmd_packet.data_bytes[33:].decode('utf-8')))
        """

        return uuid, build_date, build_time

    ###################################################################################################################
    async def appl_cmd_get_version(self):

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.GET_VERSION, bytearray(), 32)

        major = int.from_bytes(appl_cmd_packet.data_bytes[0:4], byteorder='little', signed=False)
        minor = int.from_bytes(appl_cmd_packet.data_bytes[4:8], byteorder='little', signed=False)
        patch = int.from_bytes(appl_cmd_packet.data_bytes[8:12], byteorder='little', signed=False)

        fw_version = "{0}.{1}.{2}".format(major, minor, patch)
        fw_build_date = appl_cmd_packet.data_bytes[13:24].decode('utf-8')
        fw_build_time = appl_cmd_packet.data_bytes[24:].decode('utf-8')

        """
        print("FW version: {0}.{1}.{2}".format(major, minor, patch))
        print("Build date: {0}".format(appl_cmd_packet.data_bytes[13:24].decode('utf-8')))
        print("Build time: {0}".format(appl_cmd_packet.data_bytes[24:].decode('utf-8')))
        """

        return fw_version, fw_build_date, fw_build_time

    ###################################################################################################################
    async def appl_cmd_get_device_type(self):

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.GET_DEVTYPE, bytearray(), 4)

        device_type = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        return device_type

    ###################################################################################################################
    async def appl_cmd_reboot(self, factory_reset, delay_before_reboot_ms):

        print("Reboot...")

        data_bytes = factory_reset.to_bytes(1, byteorder='little', signed=False)
        data_bytes += delay_before_reboot_ms.to_bytes(4, byteorder='little', signed=False)

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.REBOOT, data_bytes, 2)
        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

    ###################################################################################################################
    async def appl_cmd_deep_power_down(self):

        print("Deep power down...")

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.SET_SYS_DEEP_POWER_DOWN, bytearray(), 2)
        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        await self._client.disconnect()

    ###################################################################################################################
    async def appl_cmd_fw_disconnect(self, delay_before_disconnect_ms):

        data_bytes = delay_before_disconnect_ms.to_bytes(4, byteorder='little', signed=False)

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.SET_BLE_FW_DISCONNECT, data_bytes, 2)
        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

    ###################################################################################################################
    async def appl_cmd_ble_stream_output_state(self, enable):

        data_bytes = enable.to_bytes(1, byteorder='little', signed=False)

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.SET_BLE_STREAM_OUTPUT_STATE, data_bytes, 2)
        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

    ###################################################################################################################
    async def get_ble_connection_sts(self):

        print("BLE connection status get...")

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.GET_BLE_CONNECTION_STS, bytearray(), 22)

        extFrameSize = int.from_bytes(appl_cmd_packet.data_bytes[0:4], byteorder='little', signed=False)
        spsFrameSize = int.from_bytes(appl_cmd_packet.data_bytes[4:8], byteorder='little', signed=False)
        rxPhySpeed = int.from_bytes(appl_cmd_packet.data_bytes[8:12], byteorder='little', signed=False)
        txPhySpeed = int.from_bytes(appl_cmd_packet.data_bytes[12:16], byteorder='little', signed=False)
        phyStatus = int.from_bytes(appl_cmd_packet.data_bytes[16:20], byteorder='little', signed=False)
        status = int.from_bytes(appl_cmd_packet.data_bytes[20:22], byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        return extFrameSize, spsFrameSize, rxPhySpeed, txPhySpeed, phyStatus

    ###################################################################################################################
    async def appl_cmd_stream_sbc2_strain_gauge_start(self,
                                                      sensor_id,
                                                      samples_in_ble_packet,
                                                      analog_input_range,
                                                      calib_output_rate_hz,
                                                      data_output_rate_hz,
                                                      fir_filter_skip,
                                                      chop_enable,
                                                      dac_offset_mV):

        print("Stream sensor {0} SBC2 strain gauge start...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)
        data_bytes += samples_in_ble_packet.to_bytes(2, byteorder='little', signed=False)
        data_bytes += analog_input_range.to_bytes(2, byteorder='little', signed=False)
        data_bytes += calib_output_rate_hz.to_bytes(2, byteorder='little', signed=False)
        data_bytes += data_output_rate_hz.to_bytes(2, byteorder='little', signed=False)
        data_bytes += fir_filter_skip.to_bytes(1, byteorder='little', signed=False)
        data_bytes += chop_enable.to_bytes(1, byteorder='little', signed=False)
        data_bytes += dac_offset_mV.to_bytes(1, byteorder='little', signed=True)

        self._bt1_packets = 0
        self._bt2_packets = 0

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.START_STREAM, data_bytes, 2)

        status = int.from_bytes(appl_cmd_packet.data_bytes,  byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        print("Stream sensor {0} SBC2 strain gauge started.".format(sensor_id))

        return status

    ###################################################################################################################
    async def appl_cmd_stream_sbc2_strain_gauge_v2_start(self,
                                                         sensor_id,
                                                         samples_in_ble_packet,
                                                         power_mode,
                                                         channel0_en,
                                                         channel0_bipolar,
                                                         channel0_ref_source,
                                                         channel0_pga_gain,
                                                         channel0_filter_type,
                                                         channel0_reject60,
                                                         channel0_fs,
                                                         channel1_en,
                                                         channel1_bipolar,
                                                         channel1_ref_source,
                                                         channel1_pga_gain,
                                                         channel1_filter_type,
                                                         channel1_reject60,
                                                         channel1_fs,
                                                         channel2_en,
                                                         channel2_bipolar,
                                                         channel2_ref_source,
                                                         channel2_pga_gain,
                                                         channel2_filter_type,
                                                         channel2_reject60,
                                                         channel2_fs,
                                                         channel3_en,
                                                         channel3_bipolar,
                                                         channel3_ref_source,
                                                         channel3_pga_gain,
                                                         channel3_filter_type,
                                                         channel3_reject60,
                                                         channel3_fs):

        print("Stream sensor {0} SBC2 V2 strain gauge start...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)
        data_bytes += samples_in_ble_packet.to_bytes(2, byteorder='little', signed=False)
        data_bytes += power_mode.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_en.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_bipolar.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_ref_source.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_pga_gain.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_filter_type.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_reject60.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel0_fs.to_bytes(2, byteorder='little', signed=False)
        data_bytes += channel1_en.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_bipolar.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_ref_source.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_pga_gain.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_filter_type.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_reject60.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel1_fs.to_bytes(2, byteorder='little', signed=False)
        data_bytes += channel2_en.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_bipolar.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_ref_source.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_pga_gain.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_filter_type.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_reject60.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel2_fs.to_bytes(2, byteorder='little', signed=False)
        data_bytes += channel3_en.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_bipolar.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_ref_source.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_pga_gain.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_filter_type.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_reject60.to_bytes(1, byteorder='little', signed=False)
        data_bytes += channel3_fs.to_bytes(2, byteorder='little', signed=False)

        self._bt_v2_packets = 0

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.START_STREAM, data_bytes, 2)

        status = int.from_bytes(appl_cmd_packet.data_bytes,  byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        print("Stream sensor {0} SBC2 V2 strain gauge started.".format(sensor_id))

        return status

    ###################################################################################################################
    async def appl_cmd_stream_mcu_humidity_start(self, sensor_id):

        print("Stream sensor {0} MCU humidity start...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)

        self._humidity_packets = 0

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.START_STREAM, data_bytes, 2)

        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        print("Stream sensor {0} MCU humidity started.".format(sensor_id))

        return status

    ###################################################################################################################
    async def appl_cmd_stream_sbc1_accel_temperature_start(self, sensor_id):

        print("Stream sensor {0} SBC1 accelerometer temperature start...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)

        self._accel_temperature_packets = 0

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.START_STREAM, data_bytes, 2)

        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        print("Stream sensor {0} SBC1 accelerometer temperature started.".format(sensor_id))

        return status

    ###################################################################################################################
    async def appl_cmd_stream_sbc1_accel_start(self, sensor_id, samples_in_ble_packet, working_range,
                                               high_pass_filter, data_output_rate):

        print("Stream sensor {0} SBC1 accelerometer start...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)

        data_bytes += samples_in_ble_packet.to_bytes(2, byteorder='little', signed=False)
        data_bytes += working_range.to_bytes(1, byteorder='little', signed=False)
        data_bytes += high_pass_filter.to_bytes(1, byteorder='little', signed=False)
        data_bytes += data_output_rate.to_bytes(1, byteorder='little', signed=False)

        self._accel_packets = 0

        appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.START_STREAM, data_bytes, 2)

        status = int.from_bytes(appl_cmd_packet.data_bytes, byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        print("Stream sensor {0} SBC1 accelerometer started.".format(sensor_id))

        return status

    ###################################################################################################################
    async def appl_cmd_stream_stop(self, sensor_id, print_response=True):

        print("Stream sensor {0} stop...".format(sensor_id))

        data_bytes = sensor_id.to_bytes(1, byteorder='little', signed=False)

        await self.send_appl_cmd(TeenessApplCmdPacket.STOP_STREAM, data_bytes)

        packet = await self.receive_packet()

        while packet.data_bytes[0] != TeenessApplCmdPacket.CMD_REPLY:
            if packet.data_bytes[0] == TeenessApplCmdPacket.DATA_STREAM:
                if packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT:
                    self._bt_v2_packets += 1
                elif packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1:
                    self._bt1_packets += 1
                elif packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2:
                    self._bt2_packets += 1
                elif packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY:
                    self._humidity_packets += 1
                elif (packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG) or \
                        (packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW):
                    self._accel_packets += 1
                elif packet.data_bytes[1] == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE:
                    self._accel_temperature_packets += 1

            packet = await self.receive_packet(debug=False)

        appl_cmd_packet = TeenessApplCmdPacket(TeenessApplCmdPacket.STOP_STREAM, self._appl_cmd_request_id_outbound,
                                               22, packet)

        self._appl_cmd_request_id_outbound += 1

        # appl_cmd_packet = await self.exec_appl_cmd(TeenessApplCmdPacket.STOP_STREAM, data_bytes, 22)

        status = int.from_bytes(appl_cmd_packet.data_bytes[0:2],  byteorder='little', signed=False)

        if status != 0:
            raise OdTurningError("TeenessProtocol", "Status code {0} received.".format(
                status))

        no_of_ble_packets = int.from_bytes(appl_cmd_packet.data_bytes[2:6],  byteorder='little', signed=False)
        no_of_irq_samples = int.from_bytes(appl_cmd_packet.data_bytes[6:10],  byteorder='little', signed=False)
        no_of_served_samples = int.from_bytes(appl_cmd_packet.data_bytes[10:14],  byteorder='little', signed=False)
        start_time_ms = int.from_bytes(appl_cmd_packet.data_bytes[14:18],  byteorder='little', signed=False)
        stop_time_ms = int.from_bytes(appl_cmd_packet.data_bytes[18:22],  byteorder='little', signed=False)

        if print_response:
            if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE:
                print("Number of PC packets:         {0} packets".format(self._accel_temperature_packets))
            if (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG) or \
                    (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW):
                print("Number of PC packets:         {0} packets".format(self._accel_packets))
            if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY:
                print("Number of PC packets:         {0} packets".format(self._humidity_packets))
            if (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2) or \
                    (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1):
                print("Number of PC packets:         {0} packets".format(self._bt1_packets))
            if (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2) or \
                    (sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2):
                print("Number of PC packets:         {0} packets".format(self._bt2_packets))
            if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT:
                print("Number of PC packets:         {0} packets".format(self._bt_v2_packets))

            print("Number of BLE packets:        {0} packets".format(no_of_ble_packets))
            print("Number of served samples:     {0} samples".format(no_of_served_samples))
            if no_of_ble_packets > 0:
                print("Number of samples per packet: {0:.2f} samples/packet".format(no_of_served_samples / no_of_ble_packets))
            print("Number of interrupts:         {0} interrupts".format(no_of_irq_samples))
            print("Interrupt rate:               {0:.2f} irq/sec".format(no_of_irq_samples / ((stop_time_ms - start_time_ms) / 1000.0)))
            print("Sample time:                  {0:.03f} s".format(((stop_time_ms - start_time_ms) / 1000.0)))

            if no_of_served_samples > 0:
                print("Sample served rate:           {0:.2f} samples/sec, {1:.6f} sec/samples".format(
                    no_of_served_samples / ((stop_time_ms - start_time_ms) / 1000.0),
                    ((stop_time_ms - start_time_ms) / 1000.0) / no_of_served_samples))

        print("Stream sensor {0} stopped.".format(sensor_id))

        return status, no_of_ble_packets, no_of_irq_samples, no_of_served_samples, start_time_ms, stop_time_ms

    ###################################################################################################################
    def timestamp_to_us(self, timestamp_32kHz):

        return round(timestamp_32kHz * (1 / 32768.0) * 1000000.0)

    ###################################################################################################################
    def timestamp_to_s(self, timestamp_32kHz):

        return timestamp_32kHz / 32768.0

    ###################################################################################################################
    def timestamp_accelerometer_adjust_value(self, speed_selector):
        adjust_value = {
            0: 1.0/4000.0,
            1: 1.0/2000.0,
            2: 1.0/1000.0,
            3: 1.0/500.0,
            4: 1.0/250.0,
            5: 1.0/125.0,
            6: 1.0/62.5,
            7: 1.0/31.25,
            8: 1.0/15.625,
            9: 1.0/7.813,
            10: 1.0/3.906
        }

        return adjust_value.get(speed_selector)

    ###################################################################################################################
    async def appl_cmd_stream_data_recv(self):

        packet = await self.receive_packet()

        """
        print("Len: {0}".format(packet.data_length))
        for b in packet.data_bytes:
            print("{0:02X} ".format(b), end='')

        print('')
        """

        if packet.data_bytes[0] != TeenessApplCmdPacket.DATA_STREAM:
            raise OdTurningError("TeenessProtocol", "Invalid application packet type {0}. Expected {1}".format(
                packet.data_bytes[0], TeenessApplCmdPacket.DATA_STREAM))

        if packet.data_length <= 6:
            raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                packet.data_length))

        sensor_id = packet.data_bytes[1]
        timestamp = self.timestamp_to_s(int.from_bytes(packet.data_bytes[2:6], byteorder='little', signed=False))

        if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG:

            if (packet.data_length - 6) % 12 != 0:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._accel_packets += 1

            no_of_samples_in_pkt = (packet.data_length - 6) / 12
            sample_counter = 0
            sample_list = []

            while sample_counter < no_of_samples_in_pkt:

                X = int.from_bytes(packet.data_bytes[6 + (sample_counter * 12): 10 + (sample_counter * 12)], byteorder='little', signed=True)
                Y = int.from_bytes(packet.data_bytes[10 + (sample_counter * 12): 14 + (sample_counter * 12)], byteorder='little', signed=True)
                Z = int.from_bytes(packet.data_bytes[14 + (sample_counter * 12): 18 + (sample_counter * 12)], byteorder='little', signed=True)

                sample_list.append([X, Y, Z])

                sample_counter += 1

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW:

            if (packet.data_length - 6) % 12 != 0:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(

                    packet.data_length))

            self._accel_packets += 1

            no_of_samples_in_pkt = (packet.data_length - 6) / 12

            sample_counter = 0

            sample_list = []

            while sample_counter < no_of_samples_in_pkt:
                X = int.from_bytes(packet.data_bytes[6 + (sample_counter * 12): 10 + (sample_counter * 12)], byteorder='little', signed=True)
                Y = int.from_bytes(packet.data_bytes[10 + (sample_counter * 12): 14 + (sample_counter * 12)], byteorder='little', signed=True)
                Z = int.from_bytes(packet.data_bytes[14 + (sample_counter * 12): 18 + (sample_counter * 12)], byteorder='little', signed=True)

                sample_list.append([X, Y, Z])

                sample_counter += 1

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE:

            if packet.data_length != 10:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._accel_temperature_packets += 1

            sample_list = []
            temp = int.from_bytes(packet.data_bytes[6:10], byteorder='little', signed=True)

            sample_list.append([temp])

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY:

            if packet.data_length != 14:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._humidity_packets += 1

            sample_list = []
            temp = int.from_bytes(packet.data_bytes[6:10], byteorder='little', signed=True)
            humidity = int.from_bytes(packet.data_bytes[10:14], byteorder='little', signed=True)

            sample_list.append([temp, humidity])

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1:

            if (packet.data_length - 6) % 4 != 0:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._bt1_packets += 1

            no_of_samples_in_pkt = (packet.data_length - 6) / 4
            sample_counter = 0
            sample_list = []

            while sample_counter < no_of_samples_in_pkt:

                data = int.from_bytes(packet.data_bytes[6 + (sample_counter * 4): 10 + (sample_counter * 4)],byteorder='little', signed=True)

                sample_list.append([data])

                sample_counter += 1

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2:

            if (packet.data_length - 6) % 4 != 0:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._bt2_packets += 1

            no_of_samples_in_pkt = (packet.data_length - 6) / 4
            sample_counter = 0
            sample_list = []

            while sample_counter < no_of_samples_in_pkt:

                data = int.from_bytes(packet.data_bytes[6 + (sample_counter * 4): 10 + (sample_counter * 4)],byteorder='little', signed=True)

                sample_list.append([data])

                sample_counter += 1

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2, timestamp, sample_list

        elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT:

            if (packet.data_length - 6) % 4 != 0:
                raise OdTurningError("TeenessProtocol", "Invalid application packet length {0}.".format(
                    packet.data_length))

            self._bt_v2_packets += 1

            no_of_samples_in_pkt = (packet.data_length - 6) / 4
            sample_counter = 0
            sample_list = []

            while sample_counter < no_of_samples_in_pkt:

                data = int.from_bytes(packet.data_bytes[6 + (sample_counter * 4): 9 + (sample_counter * 4)],byteorder='little', signed=False)
                channel = int.from_bytes(packet.data_bytes[9 + (sample_counter * 4): 10 + (sample_counter * 4)],byteorder='little', signed=False)

                # data = int.from_bytes(packet.data_bytes[6 + (sample_counter * 4): 10 + (sample_counter * 4)],byteorder='little', signed=True)

                sample_list.append([channel, data])

                sample_counter += 1

            return TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT, timestamp, sample_list
        else:
            raise OdTurningError("TeenessProtocol", "Invalid sensor ID {0}.".format(sensor_id))
