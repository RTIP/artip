import itertools
from helpers import *
from helpers import Debugger
from config import *
from amplitude_matrix import AmplitudeMatrix
from window import Window
from debugging_config import DEBUG_CONFIGS


class DetailedFlagger:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_antennas(self, source):
        polarizations = GLOBAL_CONFIG['polarizations']
        source_config = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_config['field'])

        for polarization, scan_id in itertools.product(polarizations, scan_ids):
            if DEBUG_CONFIGS['manual_flag']:
                debugger = Debugger(self.measurement_set)
                debugger.flag_antennas(polarization, scan_id)
                debugger.flag_baselines(polarization, scan_id)

            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])
            scan_times = self.measurement_set.timesforscan(scan_id)

            ideal_median = amp_matrix.median()
            ideal_mad = amp_matrix.mad()
            print '\n*************************'
            print "Polarization =", polarization, " Scan Id=", scan_id
            print "Ideal values = { median:", ideal_median, ", mad:", ideal_mad, " }"
            print '---------------------------'

            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)

            # Sliding Window for Bad Antennas
            for antenna in unflagged_antennaids:
                filtered_matrix = amp_matrix.filter_by_antenna(antenna)
                if filtered_matrix.is_bad(ideal_median, ideal_mad):
                    self._identify_bad_time_window('Antenna', antenna, filtered_matrix.amplitude_data_matrix, ideal_mad,
                                                   ideal_median, scan_times)
            print '---------------------------'

            # Sliding Window for Baselines
            for (baseline, amplitudes) in amp_matrix.amplitude_data_matrix.items():
                self._identify_bad_time_window('Baseline', baseline, {baseline: amplitudes}, ideal_mad, ideal_median,
                                               scan_times)
            print '****************************'

    def _identify_bad_time_window(self, element_type, element_id, data_set, ideal_mad, ideal_median, scan_times):
        sliding_window = Window(data_set)
        while True:
            window_matrix = sliding_window.slide()
            if sliding_window.reached_end_of_collection(): break
            if window_matrix.is_bad(ideal_median, ideal_mad):
                start, end = sliding_window.current_position()
                print element_type, '=', element_id, ' was bad between', scan_times[
                    start], '[index=', start, '] and', scan_times[end], '[index=', end, ']'
