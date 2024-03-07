
import optparse
import plot


#######################################################################################################################
#
#######################################################################################################################
def _parse_prog_args():
    parser = optparse.OptionParser(usage="%prog [options] (-h for help)\n")

    parser.set_defaults(plot_csv_file=None)

    parser.add_option("-1", "--bt1",
                      dest="plot_csv_file_bt1",
                      help="CSV file to plot for BT1")

    parser.add_option("-2", "--bt2",
                      dest="plot_csv_file_bt2",
                      help="CSV file to plot for BT2")

    parser.add_option("-3", "--accel",
                      dest="plot_csv_file_accelerometer",
                      help="CSV file to plot for ACCELEROMETER")

    (options, argss) = parser.parse_args()

    return options, argss


#######################################################################################################################
#
#######################################################################################################################
if __name__ == '__main__':

    (opt, args) = _parse_prog_args()

    if opt.plot_csv_file_bt1 is not None:
        plt_bt1 = plot.Plot(opt.plot_csv_file_bt1)
        plt_bt1.plot_sbc2_strain_gauge(opt.plot_csv_file_bt1, False)

    if opt.plot_csv_file_bt2 is not None:
        plt_bt1 = plot.Plot(opt.plot_csv_file_bt2)
        plt_bt1.plot_sbc2_strain_gauge(opt.plot_csv_file_bt2, False)

    if opt.plot_csv_file_accelerometer is not None:
        plt_accel = plot.Plot(opt.plot_csv_file_accelerometer)
        plt_accel.plot_sbc1_accelerometer(opt.plot_csv_file_accelerometer, False)

    input("Press Enter to continue...")

