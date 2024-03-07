
import optparse
import plot


#######################################################################################################################
#
#######################################################################################################################
def _parse_prog_args():
    parser = optparse.OptionParser(usage="%prog [options] (-h for help)\n")

    parser.set_defaults(plot_csv_file=None)

    parser.add_option("-0", "--ch0",
                      dest="plot_csv_file_ch0",
                      help="CSV file to plot for SG CH0")

    parser.add_option("-1", "--ch1",
                      dest="plot_csv_file_ch1",
                      help="CSV file to plot for SG CH1")

    parser.add_option("-2", "--ch2",
                      dest="plot_csv_file_ch2",
                      help="CSV file to plot for SG CH2")

    parser.add_option("-3", "--ch3",
                      dest="plot_csv_file_ch3",
                      help="CSV file to plot for SG CH3")

    parser.add_option("-a", "--accel",
                      dest="plot_csv_file_accelerometer",
                      help="CSV file to plot for ACCELEROMETER")

    (options, argss) = parser.parse_args()

    return options, argss


#######################################################################################################################
#
#######################################################################################################################
if __name__ == '__main__':

    (opt, args) = _parse_prog_args()

    if opt.plot_csv_file_ch0 is not None:
        plt_ch0 = plot.Plot(opt.plot_csv_file_ch0)
        plt_ch0.plot_sbc2_strain_gauge(opt.plot_csv_file_ch0, "CH0", False)

    if opt.plot_csv_file_ch1 is not None:
        plt_ch1 = plot.Plot(opt.plot_csv_file_ch1)
        plt_ch1.plot_sbc2_strain_gauge(opt.plot_csv_file_ch1, "CH1", False)

    if opt.plot_csv_file_ch2 is not None:
        plt_ch2 = plot.Plot(opt.plot_csv_file_ch2)
        plt_ch2.plot_sbc2_strain_gauge(opt.plot_csv_file_ch2, "CH2", False)

    if opt.plot_csv_file_ch3 is not None:
        plt_ch3 = plot.Plot(opt.plot_csv_file_ch3)
        plt_ch3.plot_sbc2_strain_gauge(opt.plot_csv_file_ch3, "CH3", False)

    if opt.plot_csv_file_ch0 is not None and opt.plot_csv_file_ch1 is not None and opt.plot_csv_file_ch2 is not None and opt.plot_csv_file_ch3 is not None:
        plt_all_ch = plot.Plot(opt.plot_csv_file_ch0, opt.plot_csv_file_ch1, opt.plot_csv_file_ch2, opt.plot_csv_file_ch3)
        plt_all_ch.plot_sbc2_strain_gauge_all(False)

    if opt.plot_csv_file_accelerometer is not None:
        plt_accel = plot.Plot(opt.plot_csv_file_accelerometer)
        plt_accel.plot_sbc1_accelerometer(opt.plot_csv_file_accelerometer, False)

    input("Press Enter to continue...")

