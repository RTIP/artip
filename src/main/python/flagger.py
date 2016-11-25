from itertools import product
from baseline import Baseline

class Flagger:
    def __init__(self,measurement_set,config):
        self.__measurement_set = measurement_set
        self.__config = config

    def _r_based_bad_baselines(self, source):
        bad_baselines = []
        global_properties = self.__config.global_configs()
        source_properties = self.__config.get(source)
        scan_ids = self.__measurement_set.scan_ids_for(source_properties['field'])
        antenna_pairs = self.__measurement_set.baselines()

        baselines_data = product(global_properties['polarizations'],scan_ids,antenna_pairs)

        for polarization,scan_id,(antenna1,antenna2) in baselines_data:
            filter_params = {'primary_filters' : {'polarization': polarization, 'channel': source_properties['channel']},
                             'extra_filters' : {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}}
            phase_set = self.__measurement_set.get_phase_data(filter_params)
            if phase_set.is_dispersed(source_properties['r_threshold']):
                bad_baselines.append(Baseline(antenna1,antenna2,polarization,scan_id))
        return bad_baselines

    def get_bad_baselines(self):
        return self._r_based_bad_baselines('flux_calibration')