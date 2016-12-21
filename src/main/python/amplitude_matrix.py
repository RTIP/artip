from models.baseline import Baseline


class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, channel):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._scan_id = scan_id
        self._channel = channel
        self.amplitude_data_matrix = self._generate_matrix()

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
                                                   filters, ['corrected_amplitude'])['corrected_amplitude'][0][0]
                baseline = Baseline(primary_antenna, secondary_antenna)
                amplitude_data_matrix[baseline] = amplitude_data
        return amplitude_data_matrix

    def filter_by_antenna(self, antenna_id):
        return dict((baseline,amp_data) for baseline, amp_data in self.amplitude_data_matrix.iteritems() if baseline.contains(antenna_id))

