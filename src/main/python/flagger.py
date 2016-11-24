from angular_dispersion import is_dispersed
from itertools import product

class Flagger:
    def __init__(self,measurement_set,config):
        self.__dataset = measurement_set
        self.__config = config

    def get_bad_baselines(self,source):
        global_properties = self.__config.global_configs()
        source_properties = self.__config.get(source)
        scan_ids = self.__dataset.scan_ids_for(source_properties['field'])
        baselines = self.__dataset.baselines()
        bad_baselines = {}

        baselines_data = product(global_properties['polarizations'],scan_ids,baselines)
        for polarization,scan_id,(antenna1, antenna2) in baselines_data:
            filter_params = {'primary_filters' : {'polarization': polarization, 'channel': source_properties['channel']},
                             'extra_filters' : {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}}
            phase_data = self.__dataset.get_data(filter_params,['phase'])['phase'][0][0]
            if is_dispersed(phase_data, source_properties['r_threshold']):

                if not polarization in bad_baselines.keys():
                    bad_baselines[polarization] = {}
                if not scan_id in bad_baselines[polarization].keys():
                    bad_baselines[polarization][scan_id] = []
                bad_baselines[polarization][scan_id].append((antenna1, antenna2))
        return bad_baselines