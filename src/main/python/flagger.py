from itertools import product
from baseline import Baseline
from closure_phases_utility import ClosurePhaseUtil


class Flagger:
    def __init__(self, measurement_set, config):
        self.__measurement_set = measurement_set
        self.__config = config

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
        return self._r_based_bad_baselines('flux_calibration')
        # return self._closure_based_bad_baselines('~/Downloads/may14.ms') #~/Downloads/may14.ms

    def _initial_level_screening(self, antenna_ids, closure_util, doubtful_antennas, good_antennas, phase_threshold,
                                 source):
        for antenna_id in antenna_ids[::3]:
            antenna1 = antenna_id
            antenna2 = (antenna_id + 1) % len(antenna_ids)
            antenna3 = (antenna_id + 2) % len(antenna_ids)
            closure_phase = closure_util.closurePhTriads(source, [(antenna1, antenna2, antenna3)], 0, 1, "RR",
                                                         chan={"nchan": 1, "start": 100, "width": 1, "inc": 1})
            print antenna1, antenna2, antenna3, closure_phase
            if abs(closure_phase) < phase_threshold:
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

    def _closure_based_bad_baselines(self, source):
        source_properties = self.__config.get('closure_phases')
        closure_util = ClosurePhaseUtil(source)
        antenna_ids = self.__dataset.antennaids()
        phase_threshold = source_properties['closure_threshold']
        good_antennas = []
        bad_antennas = []
        doubtful_antennas = []
        self._initial_level_screening(antenna_ids, closure_util, doubtful_antennas, good_antennas, phase_threshold,
                                      source)
        if len(good_antennas) > 1:
            for antenna_id in doubtful_antennas:
                antenna1 = antenna_id
                antenna2 = good_antennas[0]
                antenna3 = good_antennas[1]
                closure_phase = closure_util.closurePhTriads(source, [(antenna1, antenna2, antenna3)], 0, 1, "RR",
                                                             chan={"nchan": 1, "start": 100, "width": 1, "inc": 1})
                if phase_threshold > abs(closure_phase):
                    print "in if", antenna1, antenna2, antenna3, closure_phase
                    good_antennas.append(antenna1)
                else:
                    bad_antennas.append(antenna1)
            doubtful_antennas = []
        else:
            print "Not good enough antennas to compare"

        print "Good Antennas", good_antennas
        print "Bad Antennas", bad_antennas
        print "Doubtful Antennas", doubtful_antennas

    def _remove_from_list(self, doubtful_antennas, antenna):
        if antenna in doubtful_antennas: doubtful_antennas.remove(antenna)
