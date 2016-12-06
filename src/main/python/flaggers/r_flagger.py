from itertools import product

from flagger import Flagger
from config import *

from models.baseline import Baseline


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
             self.identify_antennas(polarization, scan_id, channel, antenna)

    def identify_antennas(self, polarization, scan_id, channel, base_antenna):
        r_value_matrix = {}

        baselines = self.measurement_set.baselines_for(base_antenna)
        for (antenna1, antenna2) in baselines:
            filter_params = {'scan_number': scan_id, 'antenna1': antenna1.id, 'antenna2': antenna2.id}
            phase_set = self.measurement_set.get_phase_data({'start': channel}, polarization, filter_params)
            r_value = phase_set.calculate_angular_dispersion()

            another_antenna = antenna2 if base_antenna == antenna1 else antenna1

            if base_antenna.id not in r_value_matrix.keys():
                r_value_matrix[base_antenna.id] = {}
            r_value_matrix[base_antenna.id].update({another_antenna.id: r_value})

        print "Rmatrix-", r_value_matrix

        # antenna_state = base_antenna.get_state_for(polarization, scan_id)
        # for antenna, r_value in r_value_matrix[base_antenna].iteritems():
        #     print antenna, r_value
        #     if r_value < 0.3:
        #         # doubtful_antennas.add(antenna)
        #         antenna.get_state_for(polarization, scan_id).update_R_phase_status(AntennaStatus.DOUBTFUL)
            #
            # if len(doubtful_antennas) < 3:
            #     sorted_d = sorted(r_value_matrix[base_antenna].items(), key=operator.itemgetter(1))
            #     new_doubts = set(dict(sorted_d[:3]).keys())
            #     doubtful_antennas = set().union(doubtful_antennas, new_doubts)
            #
            # if len(doubtful_antennas) <= 5:  # 80% is good
            #     good_antennas.add(base_antenna)
            #
            # if len(doubtful_antennas) > 24:  # 20% is good
            #     doubtful_antennas = set()
            #     bad_antennas.add(base_antenna)
            #
            # history.add(base_antenna)
            # print good_antennas, bad_antennas, doubtful_antennas, history
            # for doubtful_antenna in doubtful_antennas:
            #     (good, bad, dbt) = self.identify_antennas(doubtful_antenna, channel, polarization, scan_id, history)
            #     good_antennas = set.union(good_antennas, good)
            #     bad_antennas = set.union(bad_antennas, bad)
            #     doubtful_antennas = set.union(doubtful_antennas, dbt)
            #     if history >= doubtful_antennas:
            #         return (good_antennas, bad_antennas, doubtful_antennas)
            #
            # return (good_antennas, bad_antennas, doubtful_antennas)
