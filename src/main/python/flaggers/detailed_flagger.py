import itertools
from helpers import *
from helpers import Debugger as debugger
from config import *
from amplitude_matrix import AmplitudeMatrix
from astropy.stats import median_absolute_deviation
from debugging_config import DEBUG_CONFIGS


class DetailedFlagger:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_antennas(self, source):
        dataset_deviations = {}
        polarizations = GLOBAL_CONFIG['polarizations']
        source_config = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_config['field'])

        for polarization, scan_id in itertools.product(polarizations, scan_ids):
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])

            if DEBUG_CONFIGS['manual_flag']: debugger().filter_matrix(amp_matrix.amplitude_data_matrix)

            ideal_median = amp_matrix.median()
            ideal_mad = amp_matrix.mad()
            print '\n*************************'
            print "Polarization =", polarization, " Scan Id=", scan_id
            print "Ideal values =>", ideal_median, " =>", ideal_mad
            print '---------------------------'

            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)

            self._filter_bad_data_for('Antenna', amp_matrix.filter_by_antenna, unflagged_antennaids, dataset_deviations,
                                      ideal_median)
            print '---------------------------'
            self._filter_bad_data_for('Time', amp_matrix.filter_by_time, range(0, amp_matrix.readings_count()),
                                      dataset_deviations,
                                      ideal_median)

            print '---------------------------'
            self._filter_bad_data_for('Baseline', amp_matrix.filter_by_baseline, amp_matrix.amplitude_data_matrix,
                                      dataset_deviations, ideal_median)
            print '****************************'

    def _filter_bad_data_for(self, element_name, filter, on_dataset, dataset_deviations, ideal_median):
        for element in on_dataset:
            filtered_matrix = filter(element)
            median = filtered_matrix.median()
            mad = filtered_matrix.mad()
            dataset_deviations[element] = abs(ideal_median - median)
        dataset_deviations_median = calculate_median(dataset_deviations.values())
        self._identify_bad_data(element_name, dataset_deviations, dataset_deviations_median)

    def _identify_bad_data(self, element_name, dataset_deviations, dataset_deviations_median):
        for element in dataset_deviations:
            deviation_ratio = (dataset_deviations[element] / dataset_deviations_median)
            if deviation_ratio > 5:
                print 'Bad ', element_name, '=', element
            elif deviation_ratio > 3:
                print 'Border line', element_name, '=', element
