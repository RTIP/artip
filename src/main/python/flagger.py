import itertools

import numpy

from closure_phase_util import ClosurePhaseUtil
from config import *
from models.baseline import Baseline


class Flagger:
    def __init__(self, measurement_set):
        self.__measurement_set = measurement_set
        self.__closure_util = ClosurePhaseUtil(measurement_set)

    def _r_based_bad_baselines(self, source):
        bad_baselines = []

        source_properties = ALL_CONFIGS[source]
        scan_ids = self.__measurement_set.scan_ids_for(source_properties['field'])
        antenna_pairs = self.__measurement_set.baselines()

        baselines_data = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids, antenna_pairs)

        for polarization, scan_id, (antenna1, antenna2) in baselines_data:
            filter_params = {'primary_filters': {'polarization': polarization, 'channel': source_properties['channel']},
                             'extra_filters': {'scan_number': scan_id, 'antenna1': antenna1, 'antenna2': antenna2}}
            phase_set = self.__measurement_set.get_phase_data(filter_params)
            if phase_set.is_dispersed(source_properties['r_threshold']):
                bad_baselines.append(Baseline(antenna1, antenna2, polarization, scan_id))
        return bad_baselines

    def get_bad_baselines(self):
        return self._r_based_bad_baselines('flux_calibration')

    def _initial_level_screening(self, antenna_ids, doubtful_antennas, good_antennas, dd):
        for antenna_id in antenna_ids[::3]:
            antenna1 = antenna_id
            antenna2 = (antenna_id + 1) % len(antenna_ids)
            antenna3 = (antenna_id + 2) % len(antenna_ids)
            closure_phase = self.__closure_util.closurePhTriads((antenna1, antenna2, antenna3), dd)
            closure_phase_std = numpy.std(closure_phase[0][0])
            closure_phase_mean = numpy.average(closure_phase[0][0])
            if abs(closure_phase_mean) < CLOSURE_PHASE_CONFIG['closure_threshold'] and closure_phase_std < 0.4:
                good_antennas.append(antenna1)
                good_antennas.append(antenna2)
                good_antennas.append(antenna3)
                self._remove_from_list(doubtful_antennas, antenna1)
                self._remove_from_list(doubtful_antennas, antenna2)
                self._remove_from_list(doubtful_antennas, antenna3)
            else:
                doubtful_antennas.append(antenna1)
                if antenna2 not in doubtful_antennas:
                    doubtful_antennas.append(antenna2)
                if antenna3 not in doubtful_antennas:
                    doubtful_antennas.append(antenna3)

    def closure_based_antenna_status(self):
        antenna_ids = self.__measurement_set.antennaids()

        scan_ids = self.__measurement_set.scan_ids_for(CLOSURE_PHASE_CONFIG['field'])

        polarization_scan_id_combination = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids)
        channel = {"start": CLOSURE_PHASE_CONFIG['channel']}

        for polarization, scan_id in polarization_scan_id_combination:
            good_antennas = []
            bad_antennas = []
            doubtful_antennas = []

            dd = self.__measurement_set.get_data(channel, polarization, scan_id)

            self._initial_level_screening(antenna_ids, doubtful_antennas, good_antennas, dd)
            if len(doubtful_antennas) > 0:
                if len(good_antennas) > 1:
                    self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                             good_antennas, dd)
                else:
                    self._antenna_status_of_all_triplet_combination(bad_antennas, dd, doubtful_antennas,
                                                                    good_antennas)

            print "Good Antennas", polarization, scan_id, good_antennas
            print "Bad Antennas", polarization, scan_id, bad_antennas
            print "Doubtful Antennas", polarization, scan_id, doubtful_antennas
        return bad_antennas

    def _antenna_status_of_all_triplet_combination(self, bad_antennas, dd, doubtful_antennas, good_antennas):
        print "Not enough good antennas to compare"
        good_antenna_tuple_list = self._find_first_good_antenna_tuple(doubtful_antennas, dd)
        if len(good_antenna_tuple_list) < 1:
            print "No good antennas found", doubtful_antennas
            bad_antennas[:] = doubtful_antennas[:]
            del doubtful_antennas[:]
        else:
            good_antennas.append(good_antenna_tuple_list[0][0])
            doubtful_antennas.remove(good_antenna_tuple_list[0][0])
            good_antennas.append(good_antenna_tuple_list[0][1])
            doubtful_antennas.remove(good_antenna_tuple_list[0][1])
            good_antennas.append(good_antenna_tuple_list[0][2])
            doubtful_antennas.remove(good_antenna_tuple_list[0][2])
            self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                     good_antennas, dd)

    def _antenna_status_as_compared_to_good(self, bad_antennas, doubtful_antennas, good_antennas, dd):
        for antenna_id in doubtful_antennas:
            antenna1 = antenna_id
            antenna2 = good_antennas[0]
            antenna3 = good_antennas[1]
            is_good_antenna = self._check_antenna_status((antenna1, antenna2, antenna3), dd)
            if is_good_antenna:
                good_antennas.append(antenna1)
            else:
                bad_antennas.append(antenna1)
        del doubtful_antennas[:]

    def _find_first_good_antenna_tuple(self, doubtful_antennas, dd):
        good_antennas = []
        for antenna_tuple in itertools.combinations(doubtful_antennas, 3):
            if self._check_antenna_status(antenna_tuple, dd):
                good_antennas.append(antenna_tuple)
                return good_antennas
        return good_antennas

    def _check_antenna_status(self, antenna_tuple, dd):
        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple, dd)
        closure_phase_std = numpy.std(closure_phase_array[0][0])
        closure_phase_avg = numpy.average(closure_phase_array[0][0])
        return CLOSURE_PHASE_CONFIG['closure_threshold'] > abs(closure_phase_avg) and closure_phase_std < 0.4

    def _remove_from_list(self, doubtful_antennas, antenna):
        if antenna in doubtful_antennas: doubtful_antennas.remove(antenna)
