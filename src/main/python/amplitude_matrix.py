from models.baseline import Baseline
from helpers import *
from astropy.stats import median_absolute_deviation


class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, channel, matrix={}):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._scan_id = scan_id
        self._channel = channel
        self.amplitude_data_matrix = matrix if len(matrix.keys()) > 0 else self._generate_matrix()

    def _generate_matrix(self):
        antennaids = self._measurement_set.unflagged_antennaids(self._polarization, self._scan_id)
        amplitude_data_matrix = {}

        # TODO remove duplicate baselines
        for antenna1 in antennaids:
            for antenna2 in antennaids:
                if antenna1 == antenna2:
                    continue
                elif antenna1 < antenna2:
                    primary_antenna = antenna1
                    secondary_antenna = antenna2
                else:
                    primary_antenna = antenna2
                    secondary_antenna = antenna1

                filters = {
                    'antenna1': primary_antenna,
                    'antenna2': secondary_antenna,
                    'scan_number': self._scan_id
                }

                amplitude_data = self._measurement_set.get_data({'start': self._channel}, self._polarization,
                                                                filters, ['corrected_amplitude'])[
                    'corrected_amplitude'][0][0]
                baseline = Baseline(primary_antenna, secondary_antenna)
                amplitude_data_matrix[baseline] = amplitude_data
        return amplitude_data_matrix

    def filter_by_antenna(self, antenna_id):
        antenna_matrix = dict((baseline, amp_data) for baseline, amp_data in self.amplitude_data_matrix.iteritems() if
                              baseline.contains(antenna_id))
        return AmplitudeMatrix(self._measurement_set, self._polarization, self._scan_id, self._channel, antenna_matrix)

    def filter_by_time(self, time_index):
        time_matrix = map(lambda baseline_amp: baseline_amp[time_index], self.amplitude_data_matrix.values())
        return AmplitudeMatrix(self._measurement_set, self._polarization, self._scan_id, self._channel,
                               {time_index: time_matrix})

    def filter_by_baseline(self, baseline):
        return AmplitudeMatrix(self._measurement_set, self._polarization, self._scan_id, self._channel,
                               {baseline: self.amplitude_data_matrix[baseline]})

    def readings_count(self):
        return len(self.amplitude_data_matrix[list(self.amplitude_data_matrix)[0]])

    def median(self):
        return calculate_median(self.amplitude_data_matrix.values())

    def mad(self):
        return median_absolute_deviation(self.amplitude_data_matrix.values())

    def is_empty(self):
        return len(self.amplitude_data_matrix.keys()) == 0
