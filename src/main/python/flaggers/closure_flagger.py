import itertools

from flagger import Flagger
from config import *
from scipy import stats
from closure_phase_util import ClosurePhaseUtil

from models.antenna_status import AntennaStatus


class ClosureFlagger(Flagger):
    def __init__(self, measurement_set):
        super(ClosureFlagger, self).__init__(measurement_set)
        self.__closure_util = ClosurePhaseUtil()

    def _initial_level_screening(self, antennas, doubtful_antenna_ids, good_antenna_ids, dd, polarization, scan_id):
        antennas_cycle = itertools.cycle(antennas)
        last_antenna_id = antennas[-1].id
        while True:
            antenna1 = antennas_cycle.next()
            antenna2 = antennas_cycle.next()
            antenna3 = antennas_cycle.next()
            if self._check_antenna_status((antenna1, antenna2, antenna3), dd):
                self._mark_antenna_as_good(antenna1, polarization, scan_id, good_antenna_ids, doubtful_antenna_ids)
                self._mark_antenna_as_good(antenna2, polarization, scan_id, good_antenna_ids, doubtful_antenna_ids)
                self._mark_antenna_as_good(antenna3, polarization, scan_id, good_antenna_ids, doubtful_antenna_ids)
            else:
                self._mark_antenna_as_doubtful(antenna1, polarization, scan_id, doubtful_antenna_ids)
                self._mark_antenna_as_doubtful(antenna2, polarization, scan_id, doubtful_antenna_ids)
                self._mark_antenna_as_doubtful(antenna3, polarization, scan_id, doubtful_antenna_ids)
            if last_antenna_id in [antenna1.id, antenna2.id, antenna3.id]:
                break

    def _mark_antenna_as_good(self, antenna, polarization, scan_id, good_antenna_ids, doubtful_antenna_ids):
        good_antenna_ids.add(antenna)
        antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
        doubtful_antenna_ids.discard(antenna)

    def _mark_antenna_as_doubtful(self, antenna, polarization, scan_id, doubtful_antenna_ids):
        antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.DOUBTFUL)
        doubtful_antenna_ids.add(antenna)

    def _antenna_status_of_all_triplet_combination(self, bad_antennas, dd, doubtful_antennas, good_antennas,
                                                   polarization, scan_id):
        print "Not enough good antennas to compare"
        good_antenna_tuple_list = self._find_first_good_antenna_tuple(doubtful_antennas, dd)
        if len(good_antenna_tuple_list) < 1:
            for da in doubtful_antennas:
                bad_antennas.add(da)
                da.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)
            doubtful_antennas.clear()
        else:
            self._mark_antenna_as_good(good_antenna_tuple_list[0][0], polarization, scan_id, good_antennas,
                                       doubtful_antennas)
            self._mark_antenna_as_good(good_antenna_tuple_list[0][1], polarization, scan_id, good_antennas,
                                       doubtful_antennas)
            self._mark_antenna_as_good(good_antenna_tuple_list[0][2], polarization, scan_id, good_antennas,
                                       doubtful_antennas)
            self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                     good_antennas, dd, polarization, scan_id)

    def _antenna_status_as_compared_to_good(self, bad_antennas, doubtful_antennas, good_antennas, dd, polarization,
                                            scan_id):
        good_antennas_list = list(good_antennas)
        for antenna in doubtful_antennas:
            antenna1 = antenna
            antenna2 = good_antennas_list[0]
            antenna3 = good_antennas_list[1]
            is_good_antenna = self._check_antenna_status((antenna1, antenna2, antenna3), dd)
            if is_good_antenna:
                good_antennas.add(antenna)
                antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
            else:
                bad_antennas.add(antenna)
                antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)
        doubtful_antennas.clear()

    def _find_first_good_antenna_tuple(self, doubtful_antennas, dd):
        good_antennas = []
        for antenna_tuple in itertools.combinations(doubtful_antennas, 3):
            if self._check_antenna_status(antenna_tuple, dd):
                good_antennas.append(antenna_tuple)
                return good_antennas
        return good_antennas

    def _check_antenna_status(self, antenna_tuple, dd):
        antenna_tuple_ids = (antenna_tuple[0].id, antenna_tuple[1].id, antenna_tuple[2].id)
        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple_ids, dd)
        percentileofscore = stats.percentileofscore(abs(closure_phase_array[0][0]),
                                                    CLOSURE_PHASE_CONFIG['closure_threshold'])
        return percentileofscore > \
               CLOSURE_PHASE_CONFIG['percentile_threshold']

    def get_bad_baselines(self):
        return self._closure_based_antenna_status()

    def _closure_based_antenna_status(self):
        antennas = self.measurement_set.antennas
        scan_ids = self.measurement_set.scan_ids_for(CLOSURE_PHASE_CONFIG['field'])

        polarization_scan_id_combination = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids)

        for polarization, scan_id in polarization_scan_id_combination:
            good_antennas = set([])
            doubtful_antennas = set([])
            bad_antennas = set([])
            data = self.measurement_set.get_data({'start': CLOSURE_PHASE_CONFIG['channel']}, polarization,
                                                 {'scan_number': scan_id},
                                                 ["antenna1", "antenna2", "phase"], True)

            self._initial_level_screening(antennas, doubtful_antennas, good_antennas, data, polarization,
                                          scan_id)
            if len(doubtful_antennas) > 0:
                if len(good_antennas) > 1:
                    self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                             good_antennas, data, polarization, scan_id)
                else:
                    self._antenna_status_of_all_triplet_combination(bad_antennas, data, doubtful_antennas,
                                                                    good_antennas, polarization, scan_id)