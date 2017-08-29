import itertools
from logger import logger
import numpy
from analysers.analyser import Analyser
from configs import config
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

    def _is_triplet_good(self, antenna_triplet, data):
        phase_data = data[self.source_config['phase_data_column']]
        closure_threshold = self.source_config['closure']['threshold'] * numpy.pi / 180
        antenna_tuple_ids = (antenna_triplet[0].id, antenna_triplet[1].id, antenna_triplet[2].id)

        if not self._phase_data_present_for_triplet(antenna_triplet, data):
            logger.debug("No data present for triplet={0}\n\n".format(antenna_triplet))
            return False

        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple_ids, phase_data, data['antenna1'],
                                                                  data['antenna2'])
        percentileofscore = stats.percentileofscore(abs(closure_phase_array[0][0]), closure_threshold)

        # Plotter.plot_pdf(closure_phase_array[0][0], antenna_tuple_ids, self.source_config['closure_threshold'],
        #                  "{0}_{1}".format(scan, polarization))
        return percentileofscore > self.source_config['closure']['percentage_of_closures']

    def identify_antennas_status(self):
        spw_polarization_scan_id_combination = []
        spw = config.GLOBAL_CONFIG['default_spw']

        for polarization in config.GLOBAL_CONFIG['polarizations']:
            scan_ids = self.measurement_set.scan_ids(self.source_config['fields'], polarization)
            spw_polarization_scan_id_combination += list(itertools.product(spw, [polarization], scan_ids))

        for spw, polarization, scan_id in spw_polarization_scan_id_combination:
            antennas = self.measurement_set.antennas(polarization, scan_id)

            logger.debug(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
            data = self.measurement_set.get_data(spw,
                                                 {'start': self.source_config['channel'],
                                                  'width': self.source_config['width']}, polarization,
                                                 {'scan_number': scan_id},
                                                 ["antenna1", "antenna2", self.source_config['phase_data_column']],
                                                 True)

            for antenna in antennas:
                if self._is_antenna_good(antenna, antennas, data):
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
                else:
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)

    def _is_antenna_good(self, antenna, antennas, data):
        good_triplets_count = 0
        remaining_antennas = minus(antennas, [antenna])
        antenna_combinations = list(itertools.combinations(remaining_antennas, 2))
        for antenna_combination in antenna_combinations:
            triplet_good = self._is_triplet_good(
                (antenna, antenna_combination[0], antenna_combination[1]), data)
            if triplet_good: good_triplets_count += 1
        percentage = (float(good_triplets_count) / float(len(antenna_combinations))) * 100

        logger.debug("Antenna={0}, total={1}, good_triplets_count={2}, Percentage={3}".format(antenna,
                                                                                              len(
                                                                                                  antenna_combinations),
                                                                                              good_triplets_count,
                                                                                              percentage))
        return percentage > self.source_config['closure']['percentage_of_good_triplets']

    def _phase_data_present_for_triplet(self, triplet, data):
        baseline_combinations = [(triplet[0].id, triplet[1].id),
                                 (triplet[1].id, triplet[2].id),
                                 (triplet[0].id, triplet[2].id)]

        return len(filter(lambda baseline: not self._phase_data_present_for_baseline(baseline, data),
                          baseline_combinations)) == 0

    def _phase_data_present_for_baseline(self, baseline, data):
        baseline = tuple(sorted(baseline))
        baseline_index_in_phase_data = \
            numpy.logical_and(data['antenna1'] == baseline[0], data['antenna2'] == baseline[1]).nonzero()[0]
        return bool(baseline_index_in_phase_data.shape[0])
