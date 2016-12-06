from itertools import product

from flagger import Flagger
from config import *
import operator
from models.baseline import Baseline
from models.antenna_status import AntennaStatus


class RFlagger(Flagger):
    def __init__(self, measurement_set):
        super(RFlagger, self).__init__(measurement_set)

    def get_bad_baselines(self):
        return self._r_based_bad_baselines('flux_calibration')

    def _r_based_bad_baselines(self, source):
        bad_baselines = []

        source_properties = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_properties['field'])
        antenna_pairs = self.measurement_set.baselines()

        baselines_data = product(GLOBAL_CONFIG['polarizations'], scan_ids, antenna_pairs)

        for polarization, scan_id, (antenna1, antenna2) in baselines_data:
            filters = {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}

            phase_set = self.measurement_set.get_phase_data({'start': source_properties['channel']}, polarization,
                                                            filters)
            if phase_set.is_dispersed(source_properties['r_threshold']):
                bad_baselines.append(Baseline(antenna1, antenna2, polarization, scan_id))
        return bad_baselines

    def optimized_r_based_bad_baselines(self, source):
        polarizations = GLOBAL_CONFIG['polarizations']
        source_properties = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_properties['field'])
        channel = source_properties['channel']
        antennas = self.measurement_set.antennas

        for polarization, scan_id, antenna in product(polarizations, scan_ids, antennas):
            _r_value_matrix = {}
            (bad, dbt) = self.identify_antennas(polarization, scan_id, channel, antenna, _r_value_matrix, set())
            print "bad=", bad
            print "dbt=", dbt

    def identify_antennas(self, polarization, scan_id, channel, base_antenna, _r_value_matrix, history):
        baselines = self.measurement_set.baselines_for(base_antenna)
        doubtful_antennas = set()
        bad_antennas = set()
        for (antenna1, antenna2) in baselines:
            # TODO: dont calculate again if present in r-matrix
            filter_params = {'scan_number': scan_id, 'antenna1': antenna1.id, 'antenna2': antenna2.id}
            phase_set = self.measurement_set.get_phase_data({'start': channel}, polarization, filter_params)
            r_value = phase_set.calculate_angular_dispersion()

            another_antenna = antenna2 if base_antenna == antenna1 else antenna1

            if base_antenna not in _r_value_matrix.keys():
                _r_value_matrix[base_antenna] = {}
            _r_value_matrix[base_antenna].update({another_antenna: r_value})

        print "Rmatrix-", _r_value_matrix

        for antenna, r_value in _r_value_matrix[base_antenna].iteritems():
            if r_value < 0.3:
                doubtful_antennas.add(antenna)
                antenna.update_state(polarization, scan_id, AntennaStatus.DOUBTFUL)


        if len(doubtful_antennas) < 3:
            sorted_d = sorted(_r_value_matrix[base_antenna].items(), key=operator.itemgetter(1))
            new_doubtful_antennas = set(dict(sorted_d[:3]).keys())
            for doubtful_antenna in new_doubtful_antennas:
                doubtful_antenna.update_state(polarization, scan_id, AntennaStatus.DOUBTFUL)

            doubtful_antennas = set().union(doubtful_antennas, new_doubtful_antennas)


        if len(doubtful_antennas) <= 5:  # 80% is good
            base_antenna.update_state(polarization, scan_id, AntennaStatus.GOOD)

        if len(doubtful_antennas) > 24:  # 20% is good
            doubtful_antennas = set()
            base_antenna.update_state(polarization, scan_id, AntennaStatus.BAD)
            bad_antennas.add(base_antenna)

        history.add(base_antenna)
        print bad_antennas, doubtful_antennas, history
        for doubtful_antenna in doubtful_antennas:
            (bad, dbt) = self.identify_antennas(polarization, scan_id, channel, doubtful_antenna, _r_value_matrix, history)
            bad_antennas = set.union(bad_antennas, bad)
            doubtful_antennas = set.union(doubtful_antennas, dbt)
            if history >= doubtful_antennas:
                return (bad_antennas, doubtful_antennas)

        return (bad_antennas, doubtful_antennas)
