from itertools import product

from flagger import Flagger
from config import *

from models.baseline import Baseline


class RFlagger(Flagger):
    def __init__(self, measurement_set):
        super(RFlagger,self).__init__(measurement_set)

    def get_bad_baselines(self):
        return self._r_based_bad_baselines('flux_calibration')

    def _r_based_bad_baselines(self, source):
        bad_baselines = []

        source_properties = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_properties['field'])
        antenna_pairs = self.measurement_set.baselines()

        baselines_data = product(GLOBAL_CONFIG['polarizations'], scan_ids, antenna_pairs)

        for polarization, scan_id, (antenna1, antenna2) in baselines_data:
            filter_params = {'primary_filters': {'polarization': polarization, 'channel': source_properties['channel']},
                             'extra_filters': {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}}
            phase_set = self.measurement_set.get_phase_data(filter_params)
            if phase_set.is_dispersed(source_properties['r_threshold']):
                bad_baselines.append(Baseline(antenna1, antenna2, polarization, scan_id))
        return bad_baselines
