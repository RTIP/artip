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
                debugger.flag_times(polarization, scan_id)

            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])

            ideal_median = amp_matrix.median()
            ideal_mad = amp_matrix.mad()
            print '\n*************************'
            print "Polarization =", polarization, " Scan Id=", scan_id
            print "Ideal values = { median:", ideal_median, ", mad:", ideal_mad, " }"
            print '---------------------------'

            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)

            self._filter_bad_data_for('Antenna', amp_matrix.filter_by_antenna, unflagged_antennaids,
                                      ideal_median, ideal_mad)
            print '---------------------------'
            # self._filter_bad_data_for('Time', amp_matrix.filter_by_time, range(0, amp_matrix.readings_count()),
            #                           dataset_deviations,
            #                           ideal_median, ideal_mad)

            # print '---------------------------'
            self._filter_bad_data_for('Baseline', amp_matrix.filter_by_baseline, amp_matrix.amplitude_data_matrix,
                                      ideal_median, ideal_mad)

            # Sliding Window
            for (baseline, amplitudes) in amp_matrix.amplitude_data_matrix.items():
                sliding_window = Window({baseline: amplitudes}, 10, 5)
                while True:
                    window_matrix = sliding_window.slide()
                    if window_matrix.is_empty(): break
                    if window_matrix.is_bad(ideal_median, ideal_mad):
                        print 'baseline=', baseline, 'Bad Window'
            print '****************************'

    def _filter_bad_data_for(self, element_name, filter, on_dataset, ideal_median, ideal_mad):
        for element in on_dataset:
            filtered_matrix = filter(element)
            if filtered_matrix.is_bad(ideal_median, ideal_mad):
                print 'Bad ', element_name, '=', element
