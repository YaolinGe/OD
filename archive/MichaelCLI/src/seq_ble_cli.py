from DataStreamPublisher import DataStreamPublisher
import asyncio

#######################################################################################################################
#
#######################################################################################################################
from od_turning_ble import OdTurningBle
from device_info_service import DeviceInfoService
from teeness_protocol import TeenessApplCmdPacket
from plot import Plot

# import asyncio
import time
import shlex
from cmd import Cmd
import msvcrt
from datetime import datetime, date
import psutil
import os


#######################################################################################################################
#
#######################################################################################################################
class _BleCli(Cmd, OdTurningBle):

    ###################################################################################################################
    def __init__(self):
        self.data_stream_publisher = DataStreamPublisher()

        Cmd.__init__(self)
        self.prompt = 'ODT_CLI> '
        self.intro = "Welcome to OD Turning BLE Command Line Tool"
        self.doc_header = "Welcome to help!"

        OdTurningBle.__init__(self, )
        OdTurningBle.__enter__(self)

    ####################################################################################################################
    def emptyline(self):
        pass

    ####################################################################################################################
    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)
        elif inp == 'h':
            return self.do_help(None)
        elif inp[0:5] == 'str2c':
            return self.do_sensor_stream2_calculate(inp[5:])
        elif inp[0:4] == 'str2':
            return self.do_sensor_stream2(inp[4:])
        elif inp[0:3] == 'str':
            return self.do_sensor_stream(inp[3:])
        elif inp[0:3] == 'sts':
            return self.do_status()
        elif inp[0:2] == 'sl':
            return self.do_scan_loop('')
        elif inp == 's':
            return self.do_scan('')
        elif inp[0:3] == 'cdt':
            return self.do_connect_disconnect_test(inp[3:])
        elif inp[0] == 'c':
            return self.do_connect(inp[2:])
        elif inp[0:3] == 'pwd':
            return self.do_deep_power_down(inp[3:])
        elif inp[0] == 'p':
            return self.do_pair(inp[2:])
        elif inp == 'dfw':
            return self.do_fw_disconnect('')
        elif inp == 'dwt':
            return self.do_disconnect_wait_test('')
        elif inp == 'd':
            return self.do_disconnect('')
        elif inp[0:3] == 'rbt':
            return self.do_reboot_test(inp[3:])
        elif inp[0:2] == 're':
            return self.do_restart(inp[2:])
        elif inp == 'di':
            return self.do_device_info('')

        print("Unrecognised command {0}".format(inp))

    ####################################################################################################################
    def do_exit(self, input):
        print("Ciao!")
        return True

    do_EOF = do_exit
    do_quit = do_exit

    ####################################################################################################################
    def help_exit(self):
        print('exit                                           Exit the application. Shorthand: x q Ctrl-D')

    help_EOF = help_exit
    help_quit = help_exit

    ####################################################################################################################
    def _reparse_args(self, args):

        try:
            self._options, self._argss = self._parser.parse_args(shlex.split(args))

        except SystemExit:  # Over ride system exit on help
            return False

        return True

    ####################################################################################################################
    def do_scan(self, args):

        self.event_loop.run_until_complete(self.scan_print_list())

    ####################################################################################################################
    def help_scan(self):
        print("scan or s                                          Scan for nearby BLE Devices")

    ####################################################################################################################
    async def _do_scan_loop(self):

        while not msvcrt.kbhit():

            await self.scan_print_list()

        msvcrt.getch()

    ####################################################################################################################
    def do_scan_loop(self, args):

        self.event_loop.run_until_complete(self._do_scan_loop())

    ####################################################################################################################
    def help_scan_loop(self):
        print("scanloop or sl                                          Scan loop for nearby BLE Devices")

    ####################################################################################################################
    async def _connect(self, pos):

        print(f"Connecting: {pos}")

        await self.connect(pos)

        print("")
        print("PC Address:        0x{0:04X}".format(
                await self.teeness_protocol.address_request(OdTurningBle.TEST_UUID)))
        print("")

        print("Device Address:    0x{0:04X}".format(
            await self.teeness_protocol.connected_devices_request()))

        print("Device Type:       {0}".format(await self.teeness_protocol.appl_cmd_get_device_type()))

        uuid, build_date, build_time = await self.teeness_protocol.appl_cmd_get_information()
        print("Device UUID:       ", end='')
        for u in uuid:
            print("{0:02X}".format(u), end='')
        print("")
        print("")

        fw_version, fw_build_date, fw_build_time = await self.teeness_protocol.appl_cmd_get_version()
        print("FW version:        {0}".format(fw_version))
        print("FW build date:     {0}".format(fw_build_date))
        print("FW build time:     {0}".format(fw_build_time))
        print("")

        extFrameSize, spsFrameSize, rxPhySpeed, txPhySpeed, phyStatus = await self.teeness_protocol.get_ble_connection_sts()

        print("Extended packet frame size: {0}".format(extFrameSize))
        print("SPS packet frame size:      {0}".format(spsFrameSize))
        print("RX PHY speed:               ", end='')
        if rxPhySpeed == 1:
            print("1 Mbps")
        elif rxPhySpeed == 2:
            print("2 Mbps")
        elif rxPhySpeed == 4:
            print("CODED")
        else:
            print("UNDEF")
        print("TX PHY speed:               ", end='')
        if txPhySpeed == 1:
            print("1 Mbps")
        elif txPhySpeed == 2:
            print("2 Mbps")
        elif txPhySpeed == 4:
            print("CODED")
        else:
            print("UNDEF")
        print("PHY status                  {0}".format(phyStatus))

    ####################################################################################################################
    def do_connect(self, args):

        pos = int(args)

        print("CONNECTION ARGS POS: {0}".format(pos))

        self.event_loop.run_until_complete(self._connect(pos))

    ####################################################################################################################
    def help_connect(self):
        print("connect or c                                       Connect to BLE device")

    ####################################################################################################################
    def do_disconnect(self, args):

        self.event_loop.run_until_complete(self.disconnect())

    ####################################################################################################################
    def help_disconnect(self):
        print("disconnect or d                                    Disconnect to BLE device")

    ####################################################################################################################
    def do_fw_disconnect(self, args):

        self.event_loop.run_until_complete(self.fw_disconnect(delay_before_disconnect_ms=1000))

    ####################################################################################################################
    def help_fw_disconnect(self):
        print("fw_disconnect or dfw                                    Disconnect to BLE device from FW side")

    ####################################################################################################################
    def do_restart(self, args):

        self.event_loop.run_until_complete(self.restart(int(args)))

    ####################################################################################################################
    def help_restart(self):
        print("restart or re                                    System restart")

    ####################################################################################################################
    def do_device_info(self, args):

        self.event_loop.run_until_complete(self._device_info_service.device_info_get())

        self.event_loop.run_until_complete(self.monitor_service.sys_status_get())

    ####################################################################################################################
    def help_device_info(self):
        print("device_info or di                                   Read SRTH device information")

    ####################################################################################################################
    async def _sensor_stream(self, log_path,
                             sg_sensor_id, sg_sibp, sg_air, sg_cor_hz, sg_dor_hz, sg_fir_skip, sg_chop_en, sg_dac_mv,
                             accel_sensor_id, accel_sibp, accel_range, accel_hpf, accel_dor,
                             accel_temp_sensor_id,
                             humidity_sensor_id):
        hm_file_name= None
        hm_log_file = None
        bt1_file_name = None
        bt1_log_file = None
        bt2_file_name = None
        bt2_log_file = None
        accel_temp_file_name = None
        accel_temp_log_file = None
        accel_file_name = None
        accel_log_file = None

        file_start_date = date.today()
        file_start_time = datetime.now()

        if humidity_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            hm_file_name = log_path + "\\HM-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime(
                "%H%M%S") + ".txt"
            hm_log_file = open(hm_file_name, "w")
            hm_log_file.write("Timestamp_S,Temperature,Humidity\n")

            await self.teeness_protocol.appl_cmd_stream_mcu_humidity_start(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY)

        if accel_temp_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            accel_temp_file_name = log_path + "\\ACT-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime(
                "%H%M%S") + ".txt"
            accel_temp_log_file = open(accel_temp_file_name, "w")
            accel_temp_log_file.write("Timestamp_S,Temperature\n")

            await self.teeness_protocol.appl_cmd_stream_sbc1_accel_temperature_start(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE)

        if sg_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            bt1_file_name = log_path + "\\BT1-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime(
                "%H%M%S") + ".txt"
            bt1_log_file = open(bt1_file_name, "w")
            bt1_log_file.write("Timestamp_S,Data\n")

            bt2_file_name = log_path + "\\BT2-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime(
                "%H%M%S") + ".txt"
            bt2_log_file = open(bt2_file_name, "w")
            bt2_log_file.write("Timestamp_S,Data\n")

            await self.teeness_protocol.appl_cmd_stream_sbc2_strain_gauge_start(
                sensor_id=sg_sensor_id,
                samples_in_ble_packet=sg_sibp,
                analog_input_range=sg_air,
                calib_output_rate_hz=sg_cor_hz,
                data_output_rate_hz=sg_dor_hz,
                fir_filter_skip=sg_fir_skip,
                chop_enable=sg_chop_en,
                dac_offset_mV=sg_dac_mv)

        if accel_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            accel_file_name = log_path + "\\ACC-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime(
                "%H%M%S") + ".txt"
            accel_log_file = open(accel_file_name, "w")
            accel_log_file.write("Timestamp_S,X,Y,Z\n")

            await self.teeness_protocol.appl_cmd_stream_sbc1_accel_start(
                sensor_id=accel_sensor_id,
                samples_in_ble_packet=accel_sibp,
                working_range = accel_range,
                high_pass_filter=accel_hpf,
                data_output_rate=accel_dor)

        await self.teeness_protocol.appl_cmd_ble_stream_output_state(True)

        # pkt_counter = 0

        while not await self.check_loop_exit():

            sensor_id, timestamp, sample_list = await self.teeness_protocol.appl_cmd_stream_data_recv()

            sample_counter = 0

            for sl in sample_list:

                if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE:
                    log_string = "{0:.05f},{1:.03f}".format(timestamp,
                                                            sl[0]/1000.0)
                    accel_temp_log_file.write(log_string + "\n")
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG:

                    log_string = "{0:.05f},{1:.06f},{2:.06f},{3:.06f}".format(
                        timestamp + sample_counter * self.teeness_protocol.timestamp_accelerometer_adjust_value(accel_dor),
                        sl[0] / 1000000.0,
                        sl[1] / 1000000.0,
                        sl[2] / 1000000.0)
                    accel_log_file.write(log_string + "\n")
                    # await self.data_stream_publisher.send_accelerometer_mG(log_string)
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW:

                    log_string = "{0:.05f},{1},{2},{3}".format(
                        timestamp + sample_counter * self.teeness_protocol.timestamp_accelerometer_adjust_value(accel_dor),
                        sl[0],
                        sl[1],
                        sl[2])
                    accel_log_file.write(log_string + "\n")
                    # await self.data_stream_publisher.send_accelerometer_raw(log_string)
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY:
                    log_string = "{0:.05f},{1:.03f},{2:.03f}".format(timestamp,
                                                                     sl[0]/1000.0,
                                                                     sl[1]/1000.0)
                    hm_log_file.write(log_string + "\n")
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1:
                    log_string = "{0:.05f},{1}".format(timestamp + sample_counter * 1.0/sg_dor_hz,
                                                            sl[0])
                    bt1_log_file.write(log_string + "\n")
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2:
                    log_string = "{0:.05f},{1}".format(timestamp + sample_counter * 1.0/sg_dor_hz,
                                                            sl[0])
                    bt2_log_file.write(log_string + "\n")
                else:
                    log_string = "Bad sensor ID: {0}".format(sensor_id)

                print("{0},{1}".format(sensor_id, log_string))

                sample_counter += 1

        print("")

        if sg_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            if (sg_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2) or \
                    (sg_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1):
                print("")
                await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1)
                bt1_log_file.flush()
                bt1_log_file.close()
                print("BT1 Log file: " + str(bt1_file_name))

            if (sg_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2) or \
                    (sg_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2):
                print("")
                await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT2)
                bt2_log_file.flush()
                bt2_log_file.close()
                print("BT2 Log file: " + str(bt2_file_name))

        print("")
        if humidity_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY)
            hm_log_file.flush()
            hm_log_file.close()
            print("HM Log file: " + str(hm_file_name))
        print("")
        if accel_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=accel_sensor_id)
            accel_log_file.flush()
            accel_log_file.close()
            print("ACC Log file: " + str(accel_file_name))
        print("")
        if accel_temp_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE)
            accel_temp_log_file.flush()
            accel_temp_log_file.close()
            print("ACT Log file: " + str(accel_temp_file_name))
        print("")

        await self.teeness_protocol.appl_cmd_ble_stream_output_state(False)

        print("")

        await asyncio.sleep(0.1)

        await self.serial_port_service.clear()

        msvcrt.getch()

        return accel_file_name, bt1_file_name, bt2_file_name

    ####################################################################################################################
    def _plot_sensor_stream_data(self, accel_file_name, sg_bt_no_of_average, bt1_file_name, bt2_file_name):

        plot_sg_bt1 = None
        plot_sg_bt2 = None
        plt_all_ch = None
        plot_accel = None

        if bt1_file_name is not None:
            plot_sg_bt1 = Plot(bt1_file_name)
            plot_sg_bt1.plot_sbc2_strain_gauge(bt1_file_name, "BT1", False, no_of_average=sg_bt_no_of_average)
        if bt2_file_name is not None:
            plot_sg_bt2 = Plot(bt2_file_name)
            plot_sg_bt2.plot_sbc2_strain_gauge(bt2_file_name, "BT2", False, no_of_average=sg_bt_no_of_average)

        if bt1_file_name is not None and bt2_file_name is not None:
            plt_all_ch = Plot(bt1_file_name,
                              bt2_file_name)
            plt_all_ch.plot_sbc2_strain_gauge_all(False)

        if accel_file_name is not None:
            plot_accel = Plot(accel_file_name)
            plot_accel.plot_sbc1_accelerometer(accel_file_name, False)

        input("Press Enter to continue...")

        # print("Press a KEY to continue...")

        # while not msvcrt.kbhit():
        #    time.sleep(0.1)

        plot_command = "python seq_plot.py "

        if bt1_file_name is not None:
            plot_sg_bt1.plot_close()
            plot_command += "-0 {0} ".format(bt1_file_name)
        if bt2_file_name is not None:
            plot_sg_bt2.plot_close()
            plot_command += "-1 {0} ".format(bt2_file_name)

        if plt_all_ch is not None:
            plt_all_ch.plot_close()

        if accel_file_name is not None:
            plot_accel.plot_close()
            plot_command += "-a {0} ".format(accel_file_name)

        print("")
        print("############################################################################################")
        print("# To plot again run command:")
        print("############################################################################################")
        print("{0}".format(plot_command))
        print("")

        return

    ####################################################################################################################
    def do_sensor_stream(self, args):

        accel_file_name, bt1_file_name, bt2_file_name = self.event_loop.run_until_complete(self._sensor_stream(

            "C:\\Log\\",

            TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2,  # TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_BT1_BT2,
            56,     # 1 - 56
            1010,   # 1010 (+-10mV), 2020 (+-20mV), 4040 (+-40mV), 8080 (+-80mV)
            150,    # CHOP SKIP Output rate
            150,    # 0    0    150 Hz to 2.048 kHz
                    # 1    0     50 Hz to 1.365 kHz
                    # 0    1    150 Hz to 7.6 kHz
                    # 1    1     50 Hz to 5.12 kHz
            False,   # FIR skip True/False
            False,   # CHOP EN True/False
            0,      # +-78 mV
            TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE,  # TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG or TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW
            18  , # Samples/BLE packet 1 - 18
            3,  # RANGE: 1= +-10G, 2= +-20G 3= +-40G
            0,  # Accelerometer high pass filter HPF_CORNER: 0=OFF, 1=24.7, 2=6.2084, 3=1.5545, 4=0.3862, 5=0.0954, 6=0.0238
            2,  # Accelerometer data ouput rate ODR_LPF: 0=4000Hz, 1=2000, 2=1000, 3=500, 4=250, 5=125, 6=62.5, 7=31.25, 8=15.625, 9=7.813 , 10=3.906
            TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE, # TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE,
            TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE, # TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY
             ))

        self._plot_sensor_stream_data(accel_file_name,
                                      16,
                                      bt1_file_name,
                                      bt2_file_name)
        return

    ####################################################################################################################
    def help_sensor_stream(self):
        print("sensor_stream or str                          Start streaming sensors")

    ####################################################################################################################
    def _sbc2_samples_per_second(self, power_mode, filter_type, fs):

        if power_mode == 0:
            clk = 76800.0
            avg = 8.0
        elif power_mode == 1:
            clk = 153600.0
            avg = 16.0
        else:
            clk = 614400.0
            avg = 16.0

        if filter_type == 0:  # SINC4
            # fADC = fCLK / (32 × FS[10:0])
            return clk / (32.0 * fs)

        elif filter_type == 2:  # SINC3
            # fADC = fCLK / (32 × FS[10:0])
            return clk / (32.0 * fs)

        elif filter_type == 4:  # FAST SETTLING SINC4
            # fADC = fCLK / (Avg × 32 × FS[10:0])
            return clk / (avg * 32 * fs)

        elif filter_type == 5:  # FAST SETTLING SINC3
            # fADC = fCLK / (Avg × 32 × FS[10:0])
            return clk / (avg * 32 * fs)
        elif filter_type == 72: # POST SPS=27.27
            return 27.27
        elif filter_type == 73:  # POST SPS=25.00
            return 25.00
        elif filter_type == 75:  # POST SPS=20.00
            return 20.00
        elif filter_type == 76:  # POST SPS=16.67
            return 16.67
        else:
            return 0

    ####################################################################################################################
    def _sbc2_v2_settling_time(self, power_mode, filter_type, fs):

        if power_mode == 0:
            clk = 76800
            avg = 8
        elif power_mode == 1:
            clk = 153600
            avg = 16
        else:
            clk = 614400
            avg = 16

        if filter_type == 0: # SINC4
            # tSETTLE = (4 × 32 × FS[10:0] + Dead time)/fCLK
            # where Dead time = 61 when FS[10:0] = 1 and 95 when FS[10:0] >1.
            if fs == 1:
                return ((4 * 32 * fs) + 61) / clk
            else:
                return ((4 * 32 * fs) + 95) / clk
        elif filter_type == 2: # SINC3
            # tSETTLE = (3 × 32 × FS[10:0] + Dead time)/fCLK
            # where Dead time = 61 when FS[10:0] = 1 and 95 FS[10:0] >1.
            if fs == 1:
                return ((3 * 32 * fs) + 61) / clk
            else:
                return ((3 * 32 * fs) + 95) / clk
        elif filter_type == 4:  # FAST SETTLING SINC4
            # tSETTLE = ((4 + Avg − 1) × 32 × FS[10:0] + Dead time)/fCLK
            # Dead time = 95
            return (((4 + avg - 1) * 32 * fs) + 95) / clk
        elif filter_type == 5:  # FAST SETTLING SINC3
            # tSETTLE = ((3 + Avg − 1) × 32 × FS[10:0] + Dead time)/ fCLK
            # Dead time = 95.
            return (((3 + avg - 1) * 32 * fs) + 95) / clk
        elif filter_type == 72:  # POST SPS=27.27
            if power_mode == 2:  # High
                return 0.038498
            elif power_mode == 1:  # Mid
                return 0.038998
            elif power_mode == 0:  # Low
                return 0.039662
            else:
                return 0.0
        elif filter_type == 73:  # POST SPS=25
            if power_mode == 2:  # High
                return 0.041831
            elif power_mode == 1:  # Mid
                return 0.042331
            elif power_mode == 0:  # Low
                return 0.042995
            else:
                return 0.0
        elif filter_type == 75:  # POST SPS=20
            if power_mode == 2:  # High
                return 0.051831
            elif power_mode == 1:  # Mid
                return 0.052331
            elif power_mode == 0:  # Low
                return 0.052995
            else:
                return 0.0
        elif filter_type == 76:  # POST SPS=16.67
            if power_mode == 2:  # High
                return 0.061831
            elif power_mode == 1:  # Mid
                return 0.062331
            elif power_mode == 0:  # Low
                return 0.062995
            else:
                return 0.0
        else:
            return 0

    ####################################################################################################################
    async def _sensor_stream2(self, log_path, sg_v2_sensor_id, sg_v2_sibp, sg_v2_pwr_mode,
                              sg_v2_ch0_en, sg_v2_ch0_bipolar, sg_v2_ch0_ref_source, sg_v2_ch0_pga_gain, sg_v2_ch0_filter_type, sg_v2_ch0_rej60, sg_v2_ch0_fs,
                              sg_v2_ch1_en, sg_v2_ch1_bipolar, sg_v2_ch1_ref_source, sg_v2_ch1_pga_gain, sg_v2_ch1_filter_type, sg_v2_ch1_rej60, sg_v2_ch1_fs,
                              sg_v2_ch2_en, sg_v2_ch2_bipolar, sg_v2_ch2_ref_source, sg_v2_ch2_pga_gain, sg_v2_ch2_filter_type, sg_v2_ch2_rej60, sg_v2_ch2_fs,
                              sg_v2_ch3_en, sg_v2_ch3_bipolar, sg_v2_ch3_ref_source, sg_v2_ch3_pga_gain, sg_v2_ch3_filter_type, sg_v2_ch3_rej60, sg_v2_ch3_fs,
                              accel_sensor_id, accel_sibp, accel_range, accel_hpf, accel_dor,
                              accel_temp_sensor_id,
                              humidity_sensor_id):

        accel_file_name=None
        accel_log_file=None
        accel_temp_file_name=None
        accel_temp_log_file=None
        hm_file_name=None
        hm_log_file=None
        sg_bt_ch0_v2_file_name=None
        sg_bt_ch0_v2_file=None
        sg_bt_ch0_counter=None
        sg_bt_ch0_settling_time=None
        sg_bt_ch0_sps=None
        sg_bt_ch1_v2_file_name=None
        sg_bt_ch1_v2_file=None
        sg_bt_ch1_counter=None
        sg_bt_ch1_settling_time=None
        sg_bt_ch1_sps=None
        sg_bt_ch2_v2_file_name=None
        sg_bt_ch2_v2_file=None
        sg_bt_ch2_counter=None
        sg_bt_ch2_settling_time=None
        sg_bt_ch2_sps=None
        sg_bt_ch3_v2_file_name=None
        sg_bt_ch3_v2_file=None
        sg_bt_ch3_counter=None
        sg_bt_ch3_settling_time=None
        sg_bt_ch3_sps=None
        sg_bt_average_settling_time = 0.0
        sg_bt_total_settling_time = 0.0

        file_start_date = date.today()
        file_start_time = datetime.now()

        if humidity_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            hm_file_name = log_path + "\\HM-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            hm_log_file = open(hm_file_name, "w")
            hm_log_file.write("Timestamp_S,Temperature,Humidity\n")

            await self.teeness_protocol.appl_cmd_stream_mcu_humidity_start(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY)

        if accel_temp_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            accel_temp_file_name = log_path + "\\ACT-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            accel_temp_log_file = open(accel_temp_file_name, "w")
            accel_temp_log_file.write("Timestamp_S,Temperature\n")

            await self.teeness_protocol.appl_cmd_stream_sbc1_accel_temperature_start(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE)

        if sg_v2_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            sg_bt_ch0_v2_file_name = log_path + "\\SG-BT-CH0-V2-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            sg_bt_ch0_v2_file = open(sg_bt_ch0_v2_file_name, "w")
            sg_bt_ch0_v2_file.write("Timestamp_S,Data\n")
            sg_bt_ch1_v2_file_name = log_path + "\\SG-BT-CH1-V2-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            sg_bt_ch1_v2_file = open(sg_bt_ch1_v2_file_name, "w")
            sg_bt_ch1_v2_file.write("Timestamp_S,Data\n")
            sg_bt_ch2_v2_file_name = log_path + "\\SG-BT-CH2-V2-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            sg_bt_ch2_v2_file = open(sg_bt_ch2_v2_file_name, "w")
            sg_bt_ch2_v2_file.write("Timestamp_S,Data\n")
            sg_bt_ch3_v2_file_name = log_path + "\\SG-BT-CH3-V2-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            sg_bt_ch3_v2_file = open(sg_bt_ch3_v2_file_name, "w")
            sg_bt_ch3_v2_file.write("Timestamp_S,Data\n")

            await self.teeness_protocol.appl_cmd_stream_sbc2_strain_gauge_v2_start(
                sensor_id=sg_v2_sensor_id,
                samples_in_ble_packet=sg_v2_sibp,
                power_mode=sg_v2_pwr_mode,
                channel0_en=sg_v2_ch0_en,
                channel0_bipolar=sg_v2_ch0_bipolar,
                channel0_ref_source=sg_v2_ch0_ref_source,
                channel0_pga_gain=sg_v2_ch0_pga_gain,
                channel0_filter_type= sg_v2_ch0_filter_type,
                channel0_reject60=sg_v2_ch0_rej60,
                channel0_fs=sg_v2_ch0_fs,
                channel1_en=sg_v2_ch1_en,
                channel1_bipolar=sg_v2_ch1_bipolar,
                channel1_ref_source=sg_v2_ch1_ref_source,
                channel1_pga_gain=sg_v2_ch1_pga_gain,
                channel1_filter_type= sg_v2_ch1_filter_type,
                channel1_reject60=sg_v2_ch1_rej60,
                channel1_fs=sg_v2_ch1_fs,
                channel2_en=sg_v2_ch2_en,
                channel2_bipolar=sg_v2_ch2_bipolar,
                channel2_ref_source=sg_v2_ch2_ref_source,
                channel2_pga_gain=sg_v2_ch2_pga_gain,
                channel2_filter_type= sg_v2_ch2_filter_type,
                channel2_reject60=sg_v2_ch2_rej60,
                channel2_fs=sg_v2_ch2_fs,
                channel3_en=sg_v2_ch3_en,
                channel3_bipolar=sg_v2_ch3_bipolar,
                channel3_ref_source=sg_v2_ch3_ref_source,
                channel3_pga_gain=sg_v2_ch3_pga_gain,
                channel3_filter_type=sg_v2_ch3_filter_type,
                channel3_reject60=sg_v2_ch3_rej60,
                channel3_fs=sg_v2_ch3_fs)

            sg_bt_ch0_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch0_filter_type, sg_v2_ch0_fs)
            sg_bt_ch1_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch1_filter_type, sg_v2_ch1_fs)
            sg_bt_ch2_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch2_filter_type, sg_v2_ch2_fs)
            sg_bt_ch3_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch3_filter_type, sg_v2_ch3_fs)

            sg_bt_no_of_ch_en = 0
            if sg_v2_ch0_en:
                sg_bt_total_settling_time += sg_bt_ch0_settling_time
                sg_bt_no_of_ch_en += 1
            if sg_v2_ch1_en:
                sg_bt_total_settling_time += sg_bt_ch1_settling_time
                sg_bt_no_of_ch_en += 1
            if sg_v2_ch2_en:
                sg_bt_total_settling_time += sg_bt_ch2_settling_time
                sg_bt_no_of_ch_en += 1
            if sg_v2_ch3_en:
                sg_bt_total_settling_time += sg_bt_ch3_settling_time
                sg_bt_no_of_ch_en += 1

            sg_bt_average_settling_time = sg_bt_total_settling_time / sg_bt_no_of_ch_en

            sg_bt_ch0_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch0_filter_type, sg_v2_ch0_fs)
            sg_bt_ch1_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch1_filter_type, sg_v2_ch1_fs)
            sg_bt_ch2_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch2_filter_type, sg_v2_ch2_fs)
            sg_bt_ch3_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch3_filter_type, sg_v2_ch3_fs)
            sg_bt_ch0_counter = 0
            sg_bt_ch1_counter = 0
            sg_bt_ch2_counter = 0
            sg_bt_ch3_counter = 0

        if accel_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            if accel_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG:
                accel_file_name = log_path + "\\ACC-mG-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"
            elif accel_sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW:
                accel_file_name = log_path + "\\ACC-RAW-Dataset-" + str(file_start_date) + "-" + file_start_time.strftime("%H%M%S") + ".txt"

            accel_log_file = open(accel_file_name, "w")
            accel_log_file.write("Timestamp_S,X,Y,Z\n")

            await self.teeness_protocol.appl_cmd_stream_sbc1_accel_start(
                sensor_id=accel_sensor_id,
                samples_in_ble_packet=accel_sibp,
                working_range = accel_range,
                high_pass_filter=accel_hpf,
                data_output_rate=accel_dor)

        await self.teeness_protocol.appl_cmd_ble_stream_output_state(True)

        while not await self.check_loop_exit():

            sensor_id, timestamp, sample_list = await self.teeness_protocol.appl_cmd_stream_data_recv()

            sample_counter = 0

            for sl in sample_list:

                log_string=""

                if sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE:
                    log_string = "{0:.05f},{1:.03f}".format(timestamp,
                                                            sl[0]/1000.0)
                    accel_temp_log_file.write(log_string + "\n")
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG:

                    log_string = "{0:.05f},{1:.06f},{2:.06f},{3:.06f}".format(
                        timestamp + sample_counter * self.teeness_protocol.timestamp_accelerometer_adjust_value(accel_dor),
                        sl[0] / 1000000.0,
                        sl[1] / 1000000.0,
                        sl[2] / 1000000.0)
                    accel_log_file.write(log_string + "\n")
                    # await self.data_stream_publisher.send_accelerometer_mG(log_string)
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW:

                    log_string = "{0:.05f},{1},{2},{3}".format(
                        timestamp + sample_counter * self.teeness_protocol.timestamp_accelerometer_adjust_value(accel_dor),
                        sl[0],
                        sl[1],
                        sl[2])
                    accel_log_file.write(log_string + "\n")
                    # await self.data_stream_publisher.send_accelerometer_raw(log_string)
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY:
                    log_string = "{0:.05f},{1:.03f},{2:.03f}".format(timestamp,
                                                                     sl[0]/1000.0,
                                                                     sl[1]/1000.0)
                    hm_log_file.write(log_string + "\n")
                elif sensor_id == TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT:

                    # ==================================================================================================
                    timestamp_common = timestamp + (sample_counter * sg_bt_average_settling_time)

                    if sl[0] == 0:
                        log_string = "{0:.05f},{1}".format(timestamp_common, sl[1])
                        sg_bt_ch0_v2_file.write(log_string + "\n")
                        await self.data_stream_publisher.send_strain_gauge_ch0(log_string)
                        sg_bt_ch0_counter += 1
                    elif sl[0] == 1:
                        log_string = "{0:.05f},{1}".format(timestamp_common, sl[1])
                        sg_bt_ch1_v2_file.write(log_string + "\n")
                        await self.data_stream_publisher.send_strain_gauge_ch1(log_string)
                        sg_bt_ch1_counter += 1
                    elif sl[0] == 2:
                        log_string = "{0:.05f},{1}".format(timestamp_common, sl[1])
                        sg_bt_ch2_v2_file.write(log_string + "\n")
                        await self.data_stream_publisher.send_strain_gauge_ch2(log_string)
                        sg_bt_ch2_counter += 1
                    elif sl[0] == 3:
                        log_string = "{0:.05f},{1}".format(timestamp_common, sl[1])
                        sg_bt_ch3_v2_file.write(log_string + "\n")
                        await self.data_stream_publisher.send_strain_gauge_ch3(log_string)
                        sg_bt_ch3_counter += 1
                    else:
                        log_string = "Bad sensor ID: {0}".format(sensor_id)
                    # ==================================================================================================

                    log_string = "{0},{1}".format(log_string, sl[0])

                print("{0},{1}".format(sensor_id, log_string))

                sample_counter += 1

        print("")

        print("")
        if humidity_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY)
            hm_log_file.flush()
            hm_log_file.close()
            print("")
            print("HM Log file: " + str(hm_file_name))
            print("")

        if accel_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=accel_sensor_id)
            accel_log_file.flush()
            accel_log_file.close()
            print("")
            print("ACC Log file: " + str(accel_file_name))
            print("")

        if accel_temp_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE)
            accel_temp_log_file.flush()
            accel_temp_log_file.close()
            print("")
            print("ACC TEMP Log file: " + str(accel_temp_file_name))
            print("")

        print("")

        if sg_v2_sensor_id != TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE:
            await self.teeness_protocol.appl_cmd_stream_stop(sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT)
            print("")
            print("SG BT CH0: Sps={0:.06f}, Settle={1:.06f}, Samples={2}".format(sg_bt_ch0_sps, sg_bt_ch0_settling_time, sg_bt_ch0_counter))
            print("SG BT CH1: Sps={0:.06f}, Settle={1:.06f}, Samples={2}".format(sg_bt_ch1_sps, sg_bt_ch1_settling_time, sg_bt_ch1_counter))
            print("SG BT CH2: Sps={0:.06f}, Settle={1:.06f}, Samples={2}".format(sg_bt_ch2_sps, sg_bt_ch2_settling_time, sg_bt_ch2_counter))
            print("SG BT CH3: Sps={0:.06f}, Settle={1:.06f}, Samples={2}".format(sg_bt_ch3_sps, sg_bt_ch3_settling_time, sg_bt_ch3_counter))
            print("SG BT TOT settle: {0:.06f}, {1:.06f}, {2:.06f}, {3:.06f}".format(sg_bt_total_settling_time, 1.0/sg_bt_total_settling_time, sg_bt_average_settling_time, 1.0/sg_bt_average_settling_time))
            print("SG BT TOT Samples: {0}".format(sg_bt_ch0_counter + sg_bt_ch1_counter + sg_bt_ch2_counter + sg_bt_ch3_counter))

            print("")
            sg_bt_ch0_v2_file.flush()
            sg_bt_ch0_v2_file.close()
            print("SG BT CH0 V2 Log file: " + str(sg_bt_ch0_v2_file_name))
            sg_bt_ch1_v2_file.flush()
            sg_bt_ch1_v2_file.close()
            print("SG BT CH1 V2 Log file: " + str(sg_bt_ch1_v2_file_name))
            sg_bt_ch2_v2_file.flush()
            sg_bt_ch2_v2_file.close()
            print("SG BT CH2 V2 Log file: " + str(sg_bt_ch2_v2_file_name))
            sg_bt_ch3_v2_file.flush()
            sg_bt_ch3_v2_file.close()
            print("SG BT CH3 V2 Log file: " + str(sg_bt_ch3_v2_file_name))

        await self.teeness_protocol.appl_cmd_ble_stream_output_state(False)

        print("")
        print("CRC ERRORS: {0}".format(self.teeness_protocol.crc_error_counter_get()))

        await asyncio.sleep(0.1)

        await self.serial_port_service.clear()

        print("")

        msvcrt.getch()

        return accel_file_name, \
            sg_bt_ch0_v2_file_name, \
            sg_bt_ch1_v2_file_name, \
            sg_bt_ch2_v2_file_name, \
            sg_bt_ch3_v2_file_name

    ####################################################################################################################
    def _plot_sensor_stream2_data(self, accel_file_name, sg_bt_no_of_average, sg_bt_ch0_v2_file_name, sg_bt_ch1_v2_file_name, sg_bt_ch2_v2_file_name, sg_bt_ch3_v2_file_name):

        plot_sg_ch0 = None
        plot_sg_ch1 = None
        plot_sg_ch2 = None
        plot_sg_ch3 = None
        plt_all_ch = None
        plot_accel = None

        if sg_bt_ch0_v2_file_name is not None:
            plot_sg_ch0 = Plot(sg_bt_ch0_v2_file_name)
            plot_sg_ch0.plot_sbc2_strain_gauge(sg_bt_ch0_v2_file_name, "CH0", False, no_of_average=sg_bt_no_of_average)
        if sg_bt_ch1_v2_file_name is not None:
            plot_sg_ch1 = Plot(sg_bt_ch1_v2_file_name)
            plot_sg_ch1.plot_sbc2_strain_gauge(sg_bt_ch1_v2_file_name, "CH1", False, no_of_average=sg_bt_no_of_average)
        if sg_bt_ch2_v2_file_name is not None:
            plot_sg_ch2 = Plot(sg_bt_ch2_v2_file_name)
            plot_sg_ch2.plot_sbc2_strain_gauge(sg_bt_ch2_v2_file_name, "CH2", False, no_of_average=sg_bt_no_of_average)
        if sg_bt_ch3_v2_file_name is not None:
            plot_sg_ch3 = Plot(sg_bt_ch3_v2_file_name)
            plot_sg_ch3.plot_sbc2_strain_gauge(sg_bt_ch3_v2_file_name, "CH3", False, no_of_average=sg_bt_no_of_average)

        if sg_bt_ch0_v2_file_name is not None and sg_bt_ch1_v2_file_name is not None and sg_bt_ch2_v2_file_name is not None and sg_bt_ch3_v2_file_name is not None:
            plt_all_ch = Plot(sg_bt_ch0_v2_file_name,
                              sg_bt_ch1_v2_file_name,
                              sg_bt_ch2_v2_file_name,
                              sg_bt_ch3_v2_file_name)
            plt_all_ch.plot_sbc2_strain_gauge_all(False)

        if accel_file_name is not None:
            plot_accel = Plot(accel_file_name)
            plot_accel.plot_sbc1_accelerometer(accel_file_name, False)

        input("Press Enter to continue...")

        # print("Press a KEY to continue...")

        # while not msvcrt.kbhit():
        #    time.sleep(0.1)

        plot_command = "python seq_plot.py "

        if sg_bt_ch0_v2_file_name is not None:
            plot_sg_ch0.plot_close()
            plot_command += "-0 {0} ".format(sg_bt_ch0_v2_file_name)
        if sg_bt_ch1_v2_file_name is not None:
            plot_sg_ch1.plot_close()
            plot_command += "-1 {0} ".format(sg_bt_ch1_v2_file_name)
        if sg_bt_ch2_v2_file_name is not None:
            plot_sg_ch2.plot_close()
            plot_command += "-2 {0} ".format(sg_bt_ch2_v2_file_name)
        if sg_bt_ch3_v2_file_name is not None:
            plot_sg_ch3.plot_close()
            plot_command += "-3 {0} ".format(sg_bt_ch3_v2_file_name)

        if plt_all_ch is not None:
            plt_all_ch.plot_close()

        if accel_file_name is not None:
            plot_accel.plot_close()
            plot_command += "-a {0} ".format(accel_file_name)

        print("")
        print("############################################################################################")
        print("# To plot again run command:")
        print("############################################################################################")
        print("{0}".format(plot_command))
        print("")

        return

    ####################################################################################################################
    def do_sensor_stream2_calculate(self, args):

        sg_v2_pwr_mode = 2  # 0=LOW, 1=MID, 2=HIGH

        sg_v2_ch0_en = True  # True for channel 0 enable else false
        sg_v2_ch0_filter_type = 5  # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
        sg_v2_ch0_fs = 13  # 1-2047

        sg_v2_ch1_en = True  # True for channel 1 enable else false
        sg_v2_ch1_filter_type = 5  # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
        sg_v2_ch1_fs = 13  # 1-2047

        sg_v2_ch2_en = True  # True for channel 2 enable else false
        sg_v2_ch2_filter_type = 5  # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
        sg_v2_ch2_fs = 13  # 1-2047

        sg_v2_ch3_en = True  # True for channel 3 enable else false
        sg_v2_ch3_filter_type = 5  # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
        sg_v2_ch3_fs = 13  # 1-2047

        sg_bt_ch0_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch0_filter_type, sg_v2_ch0_fs)
        sg_bt_ch1_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch1_filter_type, sg_v2_ch1_fs)
        sg_bt_ch2_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch2_filter_type, sg_v2_ch2_fs)
        sg_bt_ch3_settling_time = self._sbc2_v2_settling_time(sg_v2_pwr_mode, sg_v2_ch3_filter_type, sg_v2_ch3_fs)

        sg_bt_total_settling_time = 0
        sg_bt_no_of_ch_en = 0
        if sg_v2_ch0_en:
            sg_bt_total_settling_time += sg_bt_ch0_settling_time
            sg_bt_no_of_ch_en += 1
        if sg_v2_ch1_en:
            sg_bt_total_settling_time += sg_bt_ch1_settling_time
            sg_bt_no_of_ch_en += 1
        if sg_v2_ch2_en:
            sg_bt_total_settling_time += sg_bt_ch2_settling_time
            sg_bt_no_of_ch_en += 1
        if sg_v2_ch3_en:
            sg_bt_total_settling_time += sg_bt_ch3_settling_time
            sg_bt_no_of_ch_en += 1

        sg_bt_average_settling_time = sg_bt_total_settling_time / sg_bt_no_of_ch_en

        sg_bt_ch0_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch0_filter_type, sg_v2_ch0_fs)
        sg_bt_ch1_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch1_filter_type, sg_v2_ch1_fs)
        sg_bt_ch2_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch2_filter_type, sg_v2_ch2_fs)
        sg_bt_ch3_sps = self._sbc2_samples_per_second(sg_v2_pwr_mode, sg_v2_ch3_filter_type, sg_v2_ch3_fs)

        print("")

        print("SG BT CH0: Sps={0:.06f} Hz, Settle={1:.06f} Seconds, Enabled={2}".format(sg_bt_ch0_sps, sg_bt_ch0_settling_time,
                                                                             str(sg_v2_ch0_en)))
        print("SG BT CH1: Sps={0:.06f} Hz, Settle={1:.06f} Seconds, Enabled={2}".format(sg_bt_ch1_sps, sg_bt_ch1_settling_time,
                                                                             str(sg_v2_ch1_en)))
        print("SG BT CH2: Sps={0:.06f} Hz, Settle={1:.06f} Seconds, Enabled={2}".format(sg_bt_ch2_sps, sg_bt_ch2_settling_time,
                                                                             str(sg_v2_ch2_en)))
        print("SG BT CH3: Sps={0:.06f} Hz, Settle={1:.06f} Seconds, Enabled={2}".format(sg_bt_ch3_sps, sg_bt_ch3_settling_time,
                                                                             str(sg_v2_ch3_en)))
        print("")

        print("SG BT Total settle: {0:.06f} Seconds".format(sg_bt_total_settling_time))
        print("SG BT Average settle: {0:.06f} Seconds".format(sg_bt_average_settling_time))
        print("SG BT Total estimated Sps: {0:.06f} Hz".format(1.0 / sg_bt_average_settling_time))

        print("")

    ####################################################################################################################
    def do_sensor_stream2(self, args):

        accel_file_name, \
            sg_bt_ch0_v2_file_name, \
            sg_bt_ch1_v2_file_name, \
            sg_bt_ch2_v2_file_name, \
            sg_bt_ch3_v2_file_name = self.event_loop.run_until_complete(self._sensor_stream2(

                log_path="C:\\Log\\",

                sg_v2_sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT, #TeenessApplCmdPacket.STREAM_SENSOR_ID_SG_V2_BT
                sg_v2_sibp=32,       # 1-56 Samples per BLE packet
                sg_v2_pwr_mode=2,   # 0=LOW, 1=MID, 2=HIGH

                sg_v2_ch0_en=True,       # True for channel 0 enable else false
                sg_v2_ch0_bipolar=True,   # True=bipolar else False=unipolar
                sg_v2_ch0_ref_source=0,  # 0=REFIN1(+)/REFIN1(−), 2=Internal reference
                sg_v2_ch0_pga_gain=7,    # Channel gain (PGA) 0=±2.5V, 1=±1.25V, 2=±625mV, 3=±312.5mV, 4=±156.25mV, 5=±78.125mV 6=±39.06mV, 7=±19.53 mV
                sg_v2_ch0_filter_type=4, # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
                sg_v2_ch0_rej60=False,   # True for reject 60 Hz enable else false
                sg_v2_ch0_fs=48,        # 1-2047

                sg_v2_ch1_en=True,       # True for channel 1 enable else false
                sg_v2_ch1_bipolar=True,  # True=bipolar else False=unipolar
                sg_v2_ch1_ref_source=0,  # 0=REFIN1(+)/REFIN1(−), 2=Internal reference
                sg_v2_ch1_pga_gain=7,    # Channel gain (PGA) 0=±2.5V, 1=±1.25V, 2=±625mV, 3=±312.5mV, 4=±156.25mV, 5=±78.125mV 6=±39.06mV, 7=±19.53 mV
                sg_v2_ch1_filter_type=4, # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
                sg_v2_ch1_rej60=False,   # True for reject 60 Hz enable else false
                sg_v2_ch1_fs=48,        # 1-2047

                sg_v2_ch2_en=True,       # True for channel 2 enable else false
                sg_v2_ch2_bipolar=True,  # True=bipolar else False=unipolar
                sg_v2_ch2_ref_source=0,  # 0=REFIN1(+)/REFIN1(−), 2=Internal reference
                sg_v2_ch2_pga_gain=7,    # Channel gain (PGA) 0=±2.5V, 1=±1.25V, 2=±625mV, 3=±312.5mV, 4=±156.25mV, 5=±78.125mV 6=±39.06mV, 7=±19.53 mV
                sg_v2_ch2_filter_type=4, # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
                sg_v2_ch2_rej60=False,   # True for reject 60 Hz enable else false
                sg_v2_ch2_fs=48,        # 1-2047

                sg_v2_ch3_en=True,       # True for channel 3 enable else false
                sg_v2_ch3_bipolar=True,  # True=bipolar else False=unipolar
                sg_v2_ch3_ref_source=0,  # 0=REFIN1(+)/REFIN1(−), 2=Internal reference
                sg_v2_ch3_pga_gain=7,  # Channel gain (PGA) 0=±2.5V, 1=±1.25V, 2=±625mV, 3=±312.5mV, 4=±156.25mV, 5=±78.125mV 6=±39.06mV, 7=±19.53 mV
                sg_v2_ch3_filter_type=4, # 0=SINC4, 2=SINC3, 4=FAST_SETTLING_SINC4, 5=FAST_SETTLING_SINC3, 72=POST_27_27 73=POST_25, 75=POST_20, 76=POST_16_7
                sg_v2_ch3_rej60=False,   # True for reject 60 Hz enable else False
                sg_v2_ch3_fs=48,         # 1-2047

                accel_sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW,  # TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW or TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_mG
                accel_sibp=18, # Samples/BLE packet 1 - 18
                accel_range=3,  # RANGE: 1= +-10G, 2= +-20G 3= +-40G
                accel_hpf=0,  # Accelerometer high pass filter HPF_CORNER: 0=OFF, 1=24.7, 2=6.2084, 3=1.5545, 4=0.3862, 5=0.0954, 6=0.0238
                accel_dor=1,  # Accelerometer data ouput rate ODR_LPF: 0=4000Hz, 1=2000, 2=1000, 3=500, 4=250, 5=125, 6=62.5, 7=31.25, 8=15.625, 9=7.813 , 10=3.906

                accel_temp_sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE, # TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_TEMPERATURE,
                humidity_sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_NONE # TeenessApplCmdPacket.STREAM_SENSOR_ID_MCU_HUMIDITY
                ))

        self._plot_sensor_stream2_data(accel_file_name,
                                       16,
                                       sg_bt_ch0_v2_file_name,
                                       sg_bt_ch1_v2_file_name,
                                       sg_bt_ch2_v2_file_name,
                                       sg_bt_ch3_v2_file_name)

        return

    ####################################################################################################################
    def help_sensor_stream2(self):
        print("sensor_stream2 or str2                          Start streaming sensors v2")

    ####################################################################################################################
    async def _connect_disconnect_test(self, device_position):

        test_loop = 1
        exit_loop = False

        while not exit_loop:

            print("")
            print("Test loop: {0}".format(test_loop))
            print("")

            await self._connect(device_position)

            packets_managed = 0
            await self.teeness_protocol.appl_cmd_stream_sbc1_accel_start(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW,
                samples_in_ble_packet=18,
                working_range=3,
                high_pass_filter=0,
                data_output_rate=1)

            sample_time_adjust_value = self.teeness_protocol.timestamp_accelerometer_adjust_value(0)

            end_time = time.time() + 10.0

            while time.time() < end_time:

                sensor_id, timestamp, sample_list = await self.teeness_protocol.appl_cmd_stream_data_recv()

                sample_counter = 0
                log_string = ""

                for sl in sample_list:
                    #log_string = "{0:.05f},{1:.06f},{2:.06f},{3:.06f}".format(
                    #    timestamp + sample_counter * sample_time_adjust_value,
                    #    sl[0] / 1000000.0,
                    #    sl[1] / 1000000.0,
                    #    sl[2] / 1000000.0)

                    #print("{0},{1}".format(sensor_id, log_string))

                    sample_counter += 1

                packets_managed += 1

                if packets_managed % 100:
                    print(".", end='', flush=True)
                else:
                    print(".")

            print("")
            print("Number of PC packets managed: {0} packets".format(packets_managed))
            print("")

            await self.teeness_protocol.appl_cmd_stream_stop(
                sensor_id=TeenessApplCmdPacket.STREAM_SENSOR_ID_SBC1_ACCEL_RAW)

            print("")

            exit_loop = await self.check_loop_exit()

            if test_loop % 2:
                await self.disconnect()
            else:
                await self.fw_disconnect(delay_before_disconnect_ms=500)

            print("")

            await asyncio.sleep(0.5)

            test_loop += 1

        print("")
        print("Ended after test loop: {0}".format(test_loop - 1))
        print("")

        msvcrt.getch()

    ####################################################################################################################
    def do_connect_disconnect_test(self, args):

        pos = int(args)

        self.event_loop.run_until_complete(self._connect_disconnect_test(pos))

    ####################################################################################################################
    def help_connect_disconnect_test(self):
        print("con_discon or cdt                          Connect/Disconnect test")

    ####################################################################################################################
    async def _reboot_test(self, device_position):

        test_loop = 1

        await self._connect(device_position)

        while not await self.check_loop_exit():

            print("")
            print("Test loop: {0}".format(test_loop))
            print("")

            await self.restart()

            test_loop += 1

        await self.disconnect()

        print("")
        print("Ended after test loop: {0}".format(test_loop - 1))
        print("")

        msvcrt.getch()

    ####################################################################################################################
    def do_reboot_test(self, args):

        pos = int(args)

        self.event_loop.run_until_complete(self._reboot_test(pos))

    ####################################################################################################################
    def help_reboot_test(self):
        print("reboot or rbt                          Reboot test")

    ####################################################################################################################
    def do_pair(self, args):

        pos = int(args)

        self.event_loop.run_until_complete(self.pair(pos))

    ####################################################################################################################
    def help_pair(self):
        print("pair or p                          Pair device")

    ####################################################################################################################
    def do_status(self):

        sts = self.event_loop.run_until_complete(self.monitor_service.sys_status_get())

        print("STATUS: {0}".format(sts))

    ####################################################################################################################
    def help_status(self):
        print("status or sts                          Status get")

    ####################################################################################################################
    async def _disconnect_wait_test(self):

        print("")
        print("Waiting for sudden disconnects...")

        while not await self.check_loop_exit():
            await asyncio.sleep(0.5)

    ####################################################################################################################
    def do_disconnect_wait_test(self, args):

        self.event_loop.run_until_complete(self._disconnect_wait_test())

    ####################################################################################################################
    def help_disconnect_wait_test(self):
        print("disconnect_wait_test or dwt              Wait for sudden disconnects")

    ####################################################################################################################
    def do_deep_power_down(self, args):

        self.event_loop.run_until_complete(self.teeness_protocol.appl_cmd_deep_power_down())

    ####################################################################################################################
    def help_deep_power_down(self):
        print("deep_power_down or pwd                   Set system into deep power down")

#######################################################################################################################
#
#######################################################################################################################

def main():
    p = psutil.Process(os.getpid())

    p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
    # p.nice(psutil.HIGH_PRIORITY_CLASS)

    _BleCli().cmdloop()

    exit(0)


if __name__ == '__main__':
    main()


