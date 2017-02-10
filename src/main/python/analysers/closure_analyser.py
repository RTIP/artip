import itertools
import logging
import numpy
from src.main.python.analysers.analyser import Analyser
from configs.config import GLOBAL_CONFIG
from scipy import stats
from closure_phase_util import ClosurePhaseUtil
from terminal_color import Color
from models.antenna_status import AntennaStatus
from helpers import *
import random
from plotter import Plotter


class ClosureAnalyser(Analyser):
    def __init__(self, measurement_set, source):
        super(ClosureAnalyser, self).__init__(measurement_set, source)
        self.__closure_util = ClosurePhaseUtil()

    def _initial_level_screening(self, antennas, doubtful_antenna_ids, good_antenna_ids, dd, polarization, scan_id):
        antennas_cycle = itertools.cycle(antennas)
        last_antenna_id = antennas[-1].id
        while True:
            antenna1 = antennas_cycle.next()
            antenna2 = antennas_cycle.next()
            antenna3 = antennas_cycle.next()
            if self._check_antenna_status((antenna1, antenna2, antenna3), dd, scan_id, polarization):
                self._mark_antenna_as_good(antenna1, polarization, scan_id, good_antenna_ids)
                self._mark_antenna_as_good(antenna2, polarization, scan_id, good_antenna_ids)
                self._mark_antenna_as_good(antenna3, polarization, scan_id, good_antenna_ids)
            else:
                self._mark_antenna_as_doubtful(antenna1, polarization, scan_id, doubtful_antenna_ids, good_antenna_ids)
                self._mark_antenna_as_doubtful(antenna2, polarization, scan_id, doubtful_antenna_ids, good_antenna_ids)
                self._mark_antenna_as_doubtful(antenna3, polarization, scan_id, doubtful_antenna_ids, good_antenna_ids)
            if last_antenna_id in [antenna1.id, antenna2.id, antenna3.id]:
                break

    def _mark_antenna_as_good(self, antenna, polarization, scan_id, good_antenna_ids):
        antenna_state = antenna.get_state_for(polarization, scan_id)
        if antenna_state.get_closure_phase_status() is not AntennaStatus.DOUBTFUL:
            good_antenna_ids.add(antenna)
            antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)

    def _mark_antenna_as_doubtful(self, antenna, polarization, scan_id, doubtful_antenna_ids, good_antenna_ids):
        antenna_state = antenna.get_state_for(polarization, scan_id)
        if antenna_state.get_closure_phase_status() == AntennaStatus.GOOD:
            good_antenna_ids.discard(antenna)
        antenna_state.update_closure_phase_status(AntennaStatus.DOUBTFUL)
        doubtful_antenna_ids.add(antenna)

    def _antenna_status_of_all_triplet_combination(self, bad_antennas, dd, doubtful_antennas, good_antennas,
                                                   polarization, scan_id):
        print "Not enough good antennas to compare"
        good_antenna_tuple_list = self._find_first_good_antenna_tuple(doubtful_antennas, dd, scan_id, polarization)
        if len(good_antenna_tuple_list) < 1:
            for da in doubtful_antennas:
                bad_antennas.add(da)
                da.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)
            doubtful_antennas.clear()
        else:
            self._mark_antenna_as_good(good_antenna_tuple_list[0][0], polarization, scan_id, good_antennas)
            self._mark_antenna_as_good(good_antenna_tuple_list[0][1], polarization, scan_id, good_antennas)
            self._mark_antenna_as_good(good_antenna_tuple_list[0][2], polarization, scan_id, good_antennas)
            self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                     good_antennas, dd, polarization, scan_id)

    def _antenna_status_as_compared_to_good(self, bad_antennas, doubtful_antennas, good_antennas, dd, polarization,
                                            scan_id):

        good_antenna_list = list(good_antennas)
        last_antenna_id = good_antenna_list[-1].id
        for d_antenna in doubtful_antennas:
            good_antennas_cycle = itertools.cycle(good_antenna_list)
            good_count = 0
            while True:
                antenna1 = d_antenna
                antenna2 = good_antennas_cycle.next()
                antenna3 = good_antennas_cycle.next()
                is_good_antenna = self._check_antenna_status((antenna1, antenna2, antenna3), dd, scan_id,
                                                             polarization)
                if is_good_antenna:
                    good_count += 1

                if last_antenna_id in (antenna2.id, antenna3.id): break

            if float(good_count) / float(len(good_antennas)/2) > 0.7:
                good_antennas.add(d_antenna)
                d_antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
            else:
                bad_antennas.add(d_antenna)
                d_antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)


    def _find_first_good_antenna_tuple(self, doubtful_antennas, dd, scan_id, polarization):
        good_antennas = []
        for antenna_tuple in itertools.combinations(doubtful_antennas, 3):
            if self._check_antenna_status(antenna_tuple, dd, scan_id, polarization):
                good_antennas.append(antenna_tuple)
                return good_antennas
        return good_antennas

    def _check_antenna_status(self, antenna_triplet, data, scan, polarization):
        phase_data = data[self.source_config['phase_data_column']]
        closure_threshold = self.source_config['closure_threshold'] * numpy.pi / 180
        antenna_tuple_ids = (antenna_triplet[0].id, antenna_triplet[1].id, antenna_triplet[2].id)
        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple_ids, phase_data, data['antenna1'],
                                                                  data['antenna2'])
        percentileofscore = stats.percentileofscore(abs(closure_phase_array[0][0]), closure_threshold)

        if percentileofscore < self.source_config['percentile_threshold']:
            # Plotter.plot_pdf(closure_phase_array[0][0], antenna_tuple_ids, self.source_config['closure_threshold'],
            #                  "{0}_{1}".format(scan, polarization))
            logging.debug(
                "   {0}\t\t{1}\t\t\t{2}\t\t{3}".format(antenna_triplet,
                                                       round(numpy.median(closure_phase_array[0][0]), 4),
                                                       round(numpy.mean(closure_phase_array[0][0]), 4),
                                                       percentileofscore))

        return percentileofscore > \
               self.source_config['percentile_threshold']

    def identify_antennas_status(self):
        antennas = self.measurement_set.antennas
        scan_ids = self.measurement_set.scan_ids_for(self.source_config['field'])

        polarization_scan_id_combination = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids)
        logging.debug(Color.WARNING + "The antenna triplets that do not qualify threshold are as below" + Color.ENDC)
        logging.debug(
            Color.BOLD + "Antenna Triplet  Closure Phase Median  Closure Phase Mean \t Percentile above threshold " + str(
                self.source_config['percentile_threshold']) + Color.ENDC)
        for polarization, scan_id in polarization_scan_id_combination:
            good_antennas = set([])
            doubtful_antennas = set([])
            bad_antennas = set([])
            data = self.measurement_set.get_data(
                {'start': self.source_config['channel'], 'width': self.source_config['width']}, polarization,
                {'scan_number': scan_id},
                ["antenna1", "antenna2", self.source_config['phase_data_column']], True)

            self._initial_level_screening(antennas, doubtful_antennas, good_antennas, data, polarization,
                                          scan_id)
            if len(doubtful_antennas) > 0:
                if len(good_antennas) > 1:
                    self._antenna_status_as_compared_to_good(bad_antennas, doubtful_antennas,
                                                             good_antennas, data, polarization, scan_id)
                else:
                    self._antenna_status_of_all_triplet_combination(bad_antennas, data, doubtful_antennas,
                                                                    good_antennas, polarization, scan_id)
