import itertools
from baseline import Baseline
from closure_phases_utility import ClosurePhaseUtil


class Flagger:
    def __init__(self, measurement_set, config, ms_dataset):
        self.__measurement_set = measurement_set
        self.__config = config
        self.__ms_dataset = ms_dataset
        self.__closure_util = ClosurePhaseUtil(ms_dataset)
        source_properties = self.__config.get('closure_phases')
        self.__phase_threshold = source_properties['closure_threshold']

    def _r_based_bad_baselines(self, source):
        bad_baselines = []
        global_properties = self.__config.global_configs()
        source_properties = self.__config.get(source)
        scan_ids = self.__measurement_set.scan_ids_for(source_properties['field'])
        antenna_pairs = self.__measurement_set.baselines()

        baselines_data = product(global_properties['polarizations'], scan_ids, antenna_pairs)

        for polarization, scan_id, (antenna1, antenna2) in baselines_data:
            filter_params = {'primary_filters': {'polarization': polarization, 'channel': source_properties['channel']},
                             'extra_filters': {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}}
            phase_set = self.__measurement_set.get_phase_data(filter_params)
            if phase_set.is_dispersed(source_properties['r_threshold']):
                bad_baselines.append(Baseline(antenna1, antenna2, polarization, scan_id))
        return bad_baselines

    def get_bad_baselines(self):
        # return self._r_based_bad_baselines('flux_calibration')
        return self._closure_based_bad_baselines()

    def _initial_level_screening(self, antenna_ids, doubtful_antennas, good_antennas):
        for antenna_id in antenna_ids[::3]:
            antenna1 = antenna_id
            antenna2 = (antenna_id + 1) % len(antenna_ids)
            antenna3 = (antenna_id + 2) % len(antenna_ids)
            closure_phase = self.__closure_util.closurePhTriads(self.__ms_dataset, [(antenna1, antenna2, antenna3)], 0,
                                                                1, "RR",
                                                                chan={"nchan": 1, "start": 100, "width": 1, "inc": 1})
            if abs(closure_phase) < self.__phase_threshold:
                good_antennas.append(antenna1)
                good_antennas.append(antenna2)
                good_antennas.append(antenna3)
                self._remove_from_list(doubtful_antennas, antenna1)
                self._remove_from_list(doubtful_antennas, antenna2)
                self._remove_from_list(doubtful_antennas, antenna3)
            else:
                doubtful_antennas.append(antenna1)
                doubtful_antennas.append(antenna2)
                doubtful_antennas.append(antenna3)

    def _closure_based_bad_baselines(self):
        antenna_ids = self.__measurement_set.antennaids()
        good_antennas = []
        bad_antennas = []
        doubtful_antennas = []

        self._initial_level_screening(antenna_ids, doubtful_antennas, good_antennas)
        if len(good_antennas) > 1:
            self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                     good_antennas)
        else:
            print "Not good enough antennas to compare"
            good_antenna_tuple_list = self._find_first_good_antenna_tuple(antenna_ids)
            if len(good_antenna_tuple_list) < 1:
                "No good antennas found"
            else:
                good_antennas.append(good_antenna_tuple_list[0])
                good_antennas.append(good_antenna_tuple_list[1])
                good_antennas.append(good_antenna_tuple_list[2])
                self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                         good_antennas)

        print "Good Antennas", good_antennas
        print "Bad Antennas", bad_antennas
        print "Doubtful Antennas", doubtful_antennas

        return bad_antennas

    def _antenna_status_as_compared_to_good(self, bad_antennas, doubtful_antennas, good_antennas):
        for antenna_id in doubtful_antennas:
            antenna1 = antenna_id
            antenna2 = good_antennas[0]
            antenna3 = good_antennas[1]
            is_good_antenna = self._check_antenna_status((antenna1, antenna2, antenna3))
            if is_good_antenna:
                good_antennas.append(antenna1)
            else:
                bad_antennas.append(antenna1)
        del doubtful_antennas[:]

    def _find_first_good_antenna_tuple(self, antenna_ids):
        good_antennas = []
        for antenna_tuple in itertools.combinations(antenna_ids, 3):
            if self._check_antenna_status(antenna_tuple):
                return good_antennas.append(antenna_tuple)
        return good_antennas;

    def _check_antenna_status(self, antenna_tuple):
        closure_phase = self.__closure_util.closurePhTriads(self.__ms_dataset, [antenna_tuple], 0, 1, "RR",
                                                            chan={"nchan": 1, "start": 100, "width": 1, "inc": 1})
        return self.__phase_threshold > abs(closure_phase)

    def _remove_from_list(self, doubtful_antennas, antenna):
        if antenna in doubtful_antennas: doubtful_antennas.remove(antenna)
