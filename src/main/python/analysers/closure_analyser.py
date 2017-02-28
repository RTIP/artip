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

    def _is_triplet_good(self, antenna_triplet, data, scan, polarization):
        phase_data = data[self.source_config['phase_data_column']]
        closure_threshold = self.source_config['closure_threshold'] * numpy.pi / 180
        antenna_tuple_ids = (antenna_triplet[0].id, antenna_triplet[1].id, antenna_triplet[2].id)
        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple_ids, phase_data, data['antenna1'],
                                                                  data['antenna2'])
        percentileofscore = stats.percentileofscore(abs(closure_phase_array[0][0]), closure_threshold)

        # Plotter.plot_pdf(closure_phase_array[0][0], antenna_tuple_ids, self.source_config['closure_threshold'],
        #                  "{0}_{1}".format(scan, polarization))

        return percentileofscore > self.source_config['percentage_of_closures']

    def identify_antennas_status(self):
        scan_ids = self.measurement_set.scan_ids_for(self.source_config['fields'])

        polarization_scan_id_combination = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids)
        for polarization, scan_id in polarization_scan_id_combination:
            antennas = self.measurement_set.get_antennas(polarization, scan_id)

            logging.debug(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
            data = self.measurement_set.get_data(
                {'start': self.source_config['channel'], 'width': self.source_config['width']}, polarization,
                {'scan_number': scan_id},
                ["antenna1", "antenna2", self.source_config['phase_data_column']], True)

            for antenna in antennas:
                if self._is_antenna_good(antenna, antennas, data, polarization, scan_id):
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
                else:
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)

    def _is_antenna_good(self, antenna, antennas, data, polarization, scan_id):
        good_triplets_count = 0
        remaining_antennas = minus(antennas, [antenna])
        antenna_combinations = list(itertools.combinations(remaining_antennas, 2))
        for antenna_combination in antenna_combinations:
            triplet_good = self._is_triplet_good(
                (antenna, antenna_combination[0], antenna_combination[1]), data, scan_id, polarization)
            if triplet_good: good_triplets_count += 1
        percentage = (float(good_triplets_count) / float(len(antenna_combinations))) * 100

        logging.debug("Antenna={0}, total={1}, good_triplets_count={2}, Percentage={3}".format(antenna,
                                                                                               len(
                                                                                                   antenna_combinations),
                                                                                               good_triplets_count,
                                                                                               percentage))

        return percentage > self.source_config['percentage_of_triplets']
