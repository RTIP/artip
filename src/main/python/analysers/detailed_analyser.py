import logging
from helpers import *
from amplitude_matrix import AmplitudeMatrix
from window import Window
from configs.pipeline_config import PIPELINE_CONFIGS
from casa.flag_reasons import BAD_ANTENNA_TIME, BAD_BASELINE_TIME
from terminal_color import Color


class DetailedAnalyser:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def analyse_antennas(self, polarization_and_scan_product, source_config, debugger):
        logging.info(Color.HEADER + "Started detailed flagging on all unflagged antennas" + Color.ENDC)
        bad_window_present = False
        for polarization, scan_id in polarization_and_scan_product:
            if PIPELINE_CONFIGS['manual_flag']: debugger.flag_antennas(polarization, scan_id)
            scan_times = self.measurement_set.timesforscan(scan_id)
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])
            global_median = amp_matrix.median()
            global_mad = amp_matrix.mad()
            self._print_polarization_details(global_mad, global_median, polarization, scan_id)

            antennaids = self.measurement_set.antenna_ids(polarization, scan_id)

            # Sliding Window for Bad Antennas
            for antenna in antennaids:
                filtered_matrix = amp_matrix.filter_by_antenna(antenna)
                if filtered_matrix.is_bad(global_median, global_mad):
                    logging.info(
                            Color.FAIL + 'Antenna ' + str(
                                    antenna) + ' is Bad running sliding Window on it' + Color.ENDC)
                    flagged_bad_window = self._flag_bad_time_window(BAD_ANTENNA_TIME, antenna,
                                                                    filtered_matrix.amplitude_data_matrix,
                                                                    global_mad,
                                                                    global_median, scan_times, polarization, scan_id)
                    if flagged_bad_window: bad_window_present = True

        return bad_window_present

    def analyse_baselines(self, polarization_and_scan_product, source_config, debugger):
        bad_window_present = False
        logging.info(Color.HEADER + "Started detailed flagging on all baselines" + Color.ENDC)
        for polarization, scan_id in polarization_and_scan_product:
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])
            global_median = amp_matrix.median()
            global_mad = amp_matrix.mad()
            scan_times = self.measurement_set.timesforscan(scan_id)
            self._print_polarization_details(global_mad, global_median, polarization, scan_id)

            # Sliding Window for Baselines
            for (baseline, amplitudes) in amp_matrix.amplitude_data_matrix.items():
                flagged_bad_window = self._flag_bad_time_window(BAD_BASELINE_TIME, baseline, {baseline: amplitudes},
                                                                global_mad, global_median,
                                                                scan_times, polarization, scan_id)
                if flagged_bad_window: bad_window_present = True

        return bad_window_present

    def _flag_bad_time_window(self, reason, element_id, data_set, global_mad, global_median, scan_times, polarization,
                              scan_id):
        bad_window_found = False
        sliding_window = Window(data_set)
        while True:
            window_matrix = sliding_window.slide()
            if window_matrix.is_empty() or sliding_window.reached_end_of_collection(): break
            if window_matrix.is_bad(global_median, global_mad):
                bad_window_found = True
                start, end = sliding_window.current_position()
                bad_timerange = scan_times[start], scan_times[end]
                if reason == BAD_ANTENNA_TIME:
                    self.measurement_set.flag_bad_antenna_time(polarization, scan_id, element_id, bad_timerange)
                    logging.debug('Antenna=' + str(element_id) + ' was bad between' + scan_times[
                        start] + '[index=' + str(start) + '] and' + scan_times[end] + '[index=' + str(end) + ']\n')
                else:
                    self.measurement_set.flag_bad_baseline_time(polarization, scan_id, element_id, bad_timerange)
                    logging.debug('Baseline=' + str(element_id) + ' was bad between' + scan_times[
                        start] + '[index=' + str(start) + '] and' + scan_times[end] + '[index=' + str(end) + ']\n')
        return bad_window_found

    def _print_polarization_details(self, global_mad, global_median, polarization, scan_id):
        logging.info(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
        logging.debug(
            Color.BACKGROUD_WHITE + "Ideal values = { median:" + str(global_median) + ", mad:" + str(
                        global_mad) + " }" + Color.ENDC)
