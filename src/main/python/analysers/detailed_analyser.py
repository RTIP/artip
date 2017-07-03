from logger import logger
from amplitude_matrix import AmplitudeMatrix
from window import Window
from casa.flag_reasons import BAD_ANTENNA_TIME, BAD_BASELINE_TIME, BAD_TIME
from terminal_color import Color


class DetailedAnalyser:
    def __init__(self, measurement_set, source_config):
        self.measurement_set = measurement_set
        self._source_config = source_config

    def analyse_time(self, spw_polarization_and_scan_product):
        logger.info(Color.HEADER + "Started detailed flagging on all unflagged antennas" + Color.ENDC)
        for spw, polarization, scan_id in spw_polarization_and_scan_product:
            scan_times = self.measurement_set.timesforscan(scan_id)
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, spw, self._source_config)
            global_median = amp_matrix.median()
            global_sigma = amp_matrix.mad_sigma()
            self._print_polarization_details(global_sigma, global_median, polarization, scan_id)

            window_config = self._source_config['detail_flagging']['time']['sliding_window']
            # Sliding Window for Time
            self._flag_bad_time_window(BAD_TIME, None, amp_matrix.amplitude_data_matrix,
                                       global_sigma, global_median,
                                       scan_times, polarization, scan_id, window_config)

        return True

    def analyse_antennas(self, spw_polarization_and_scan_product):
        logger.info(Color.HEADER + "Started detailed flagging on all unflagged antennas" + Color.ENDC)
        bad_window_present = False
        for spw, polarization, scan_id in spw_polarization_and_scan_product:
            scan_times = self.measurement_set.timesforscan(scan_id)
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, spw, self._source_config)
            global_median = amp_matrix.median()
            global_sigma = amp_matrix.mad_sigma()
            self._print_polarization_details(global_sigma, global_median, polarization, scan_id)

            antennaids = self.measurement_set.antenna_ids(polarization, scan_id)

            window_config = self._source_config['detail_flagging']['antenna']['sliding_window']
            # Sliding Window for Bad Antennas
            for antenna in antennaids:
                filtered_matrix = amp_matrix.filter_by_antenna(antenna)
                if filtered_matrix.is_bad(global_median, window_config['mad_scale_factor'] * global_sigma):
                    logger.info(
                        Color.FAIL + 'Antenna ' + str(
                            antenna) + ' is Bad running sliding Window on it' + Color.ENDC)
                    flagged_bad_window = self._flag_bad_time_window(BAD_ANTENNA_TIME, antenna,
                                                                    filtered_matrix.amplitude_data_matrix,
                                                                    global_sigma,
                                                                    global_median, scan_times, polarization, scan_id,
                                                                    window_config)
                    if flagged_bad_window: bad_window_present = True

        return bad_window_present

    def analyse_baselines(self, spw_polarization_and_scan_product):
        bad_window_present = False
        logger.info(Color.HEADER + "Started detailed flagging on all baselines" + Color.ENDC)
        for spw, polarization, scan_id in spw_polarization_and_scan_product:
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, spw, self._source_config)
            global_median = amp_matrix.median()
            global_sigma = amp_matrix.mad_sigma()
            scan_times = self.measurement_set.timesforscan(scan_id)
            self._print_polarization_details(global_sigma, global_median, polarization, scan_id)

            window_config = self._source_config['detail_flagging']['baseline']['sliding_window']
            # Sliding Window for Baselines
            for (baseline, amplitudes) in amp_matrix.amplitude_data_matrix.items():
                flagged_bad_window = self._flag_bad_time_window(BAD_BASELINE_TIME, baseline, {baseline: amplitudes},
                                                                global_sigma, global_median,
                                                                scan_times, polarization, scan_id, window_config)
                if flagged_bad_window: bad_window_present = True

        return bad_window_present

    def _flag_bad_time_window(self, reason, element_id, data_set, global_sigma, global_median, scan_times, polarization,
                              scan_id, window_config):
        bad_window_found = False
        sliding_window = Window(data_set, window_config)
        while True:
            window_matrix = sliding_window.slide()
            if window_matrix.is_bad(global_median, window_config['mad_scale_factor'] * global_sigma):
                bad_window_found = True
                start, end = sliding_window.current_position()
                bad_timerange = scan_times[start], scan_times[end]

                if reason == BAD_TIME:
                    self.measurement_set.flag_bad_time(polarization, scan_id, bad_timerange)
                    logger.debug('Time=' + ' was bad between' + scan_times[
                        start] + '[index=' + str(start) + '] and ' + scan_times[end] + '[index=' + str(end) + ']\n')

                elif reason == BAD_ANTENNA_TIME:
                    self.measurement_set.flag_bad_antenna_time(polarization, scan_id, element_id, bad_timerange)
                    logger.debug('Antenna=' + str(element_id) + ' was bad between' + scan_times[
                        start] + '[index=' + str(start) + '] and ' + scan_times[end] + '[index=' + str(end) + ']\n')
                else:
                    self.measurement_set.flag_bad_baseline_time(polarization, scan_id, element_id, bad_timerange)
                    logger.debug('Baseline=' + str(element_id) + ' was bad between' + scan_times[
                        start] + '[index=' + str(start) + '] and ' + scan_times[end] + '[index=' + str(end) + ']\n')

            if sliding_window.reached_end_of_collection(): break
        return bad_window_found

    def _print_polarization_details(self, global_sigma, global_median, polarization, scan_id):
        logger.info(
            Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
        logger.debug(
            Color.BACKGROUD_WHITE + "Ideal values = { median:" + str(global_median) + ", sigma:" + str(
                global_sigma) + " }" + Color.ENDC)
