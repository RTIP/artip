from models.baseline import Baseline
from helpers import *
from astropy.stats import median_absolute_deviation
import numpy


class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, channel, matrix={}):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._scan_id = scan_id
        self._channel = channel
        self.amplitude_data_matrix = self._generate_matrix() if measurement_set else matrix

    def _generate_matrix(self):
        antennaids = self._measurement_set.unflagged_antennaids(self._polarization, self._scan_id)
        flagged_data = self._measurement_set.flag_data[self._polarization][self._scan_id]
        amplitude_data_matrix = {}

        # TODO remove duplicate baselines
        for antenna1 in antennaids:
            for antenna2 in antennaids:
                if antenna1 < antenna2:
                    primary_antenna = antenna1
                    secondary_antenna = antenna2
                else:
                    primary_antenna = antenna2
                    secondary_antenna = antenna1

                if primary_antenna == secondary_antenna or \
                        ([primary_antenna, secondary_antenna] in flagged_data['baselines']):
                    continue

                filters = {
                    'antenna1': primary_antenna,
                    'antenna2': secondary_antenna,
                    'scan_number': self._scan_id
                }

                amplitude_data = self._measurement_set.get_data({'start': self._channel}, self._polarization,
                                                                filters, ['corrected_amplitude'])[
                    'corrected_amplitude'][0][0]
                baseline = Baseline(primary_antenna, secondary_antenna)

                if DEBUG_CONFIGS['manual_flag']:
                    amplitude_data_matrix[baseline] = delete_indexes(amplitude_data, flagged_data['times']) if \
                        DEBUG_CONFIGS['manual_flag'] else amplitude_data
        return amplitude_data_matrix

    def filter_by_antenna(self, antenna_id):
        antenna_matrix = dict((baseline, amp_data) for baseline, amp_data in self.amplitude_data_matrix.iteritems() if
                              baseline.contains(antenna_id))

        return AmplitudeMatrix(None, None, None, None, antenna_matrix)

    def filter_by_time(self, time_index):
        time_matrix = map(lambda baseline_amp: baseline_amp[time_index], self.amplitude_data_matrix.values())
        return AmplitudeMatrix(None, None, None, None,
                               {time_index: time_matrix})

    def filter_by_baseline(self, baseline):
        return AmplitudeMatrix(None, None, None, None,
                               {baseline: self.amplitude_data_matrix[baseline]})

    def readings_count(self):
        return len(self.amplitude_data_matrix[list(self.amplitude_data_matrix)[0]])

    def median(self):
        return calculate_median(self.amplitude_data_matrix.values())

    def mad(self):
        return median_absolute_deviation(self.amplitude_data_matrix.values())

    def is_empty(self):
        return len(numpy.array(self.amplitude_data_matrix.values()).flatten()) == 0

    def is_bad(self, ideal_median, ideal_mad):
        matrix_median = self.median()
        matrix_mad = self.mad()
        return self._deviated_median(ideal_median, ideal_mad, matrix_median) or self._scattered_amplitude(ideal_mad,
                                                                                                          matrix_mad)

    def _deviated_median(self, ideal_median, ideal_mad, actual_median):
        return abs(actual_median - ideal_median) > (2 * ideal_mad)

    def _scattered_amplitude(self, ideal_mad, actual_mad):
        return actual_mad > (2 * ideal_mad)
