import itertools
import numpy
from scipy import stats
from closure_phase_util import ClosurePhaseUtil
from artip.configs import config
from artip.utilities.terminal_color import Color
from artip.utilities.logger import logger
from artip.utilities.helpers import calculate_percentage,minus
from artip.analysers.analyser import Analyser
from artip.models.calib_params import CalibParams
from artip.models.antenna_status import AntennaStatus


class ClosureAnalyser(Analyser):
    def __init__(self, measurement_set, source):
        super(ClosureAnalyser, self).__init__(measurement_set, source)
        self.__closure_util = ClosurePhaseUtil()

    def _is_triplet_good(self, antenna_triplet, data):
        closure_threshold = self.source_config['closure']['threshold'] * numpy.pi / 180
        antenna_tuple_ids = (antenna_triplet[0].id, antenna_triplet[1].id, antenna_triplet[2].id)

        closure_phase_array = self.__closure_util.closurePhTriads(antenna_tuple_ids, data)

        percentileofscore = stats.percentileofscore(abs(closure_phase_array), closure_threshold)

        return percentileofscore > self.source_config['closure']['percentage_of_closures']

    def identify_antennas_status(self):
        spw_polarization_scan_id_combination = []
        spw = config.GLOBAL_CONFIGS['default_spw']

        for polarization in config.GLOBAL_CONFIGS['polarizations']:
            scan_ids = self.measurement_set.scan_ids(self.source_ids, polarization)
            spw_polarization_scan_id_combination += list(itertools.product(spw, [polarization], scan_ids))

        for spw, polarization, scan_id in spw_polarization_scan_id_combination:
            antennas = self.measurement_set.antennas(polarization, scan_id)
            calib_params = CalibParams(*self.source_config['calib_params'])

            logger.debug(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
            visibility_data = self.measurement_set.get_data(spw,
                                                            {'start': calib_params.channel,
                                                             'width': calib_params.width}, polarization,
                                                            {'scan_number': scan_id},
                                                            ["antenna1", "antenna2",
                                                             self.source_config['phase_data_column'], 'flag'])

            for antenna in antennas:
                if self._is_antenna_good(antenna, antennas, visibility_data):
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.GOOD)
                else:
                    antenna.get_state_for(polarization, scan_id).update_closure_phase_status(AntennaStatus.BAD)

    def _is_antenna_good(self, antenna, antennas, data):
        good_triplets_count = 0
        triplets_with_missing_data_count = 0
        remaining_antennas = minus(antennas, [antenna])
        antenna_combinations = list(itertools.combinations(remaining_antennas, 2))

        for antenna_combination in antenna_combinations:
            antenna_triplet = (antenna, antenna_combination[0], antenna_combination[1])
            if data.phase_data_present_for_triplet(antenna_triplet):
                triplet_good = self._is_triplet_good(antenna_triplet, data)
                if triplet_good: good_triplets_count += 1
            else:
                triplets_with_missing_data_count += 1
        total_triplets_count = len(antenna_combinations) - triplets_with_missing_data_count

        percentage = calculate_percentage(good_triplets_count, total_triplets_count)

        if total_triplets_count == 0:
            logger.debug("Antenna={0} was flagged".format(antenna))
        else:
            logger.debug("Antenna={0}, total={1}, good_triplets_count={2}, Percentage={3}".format(antenna,
                                                                                                  total_triplets_count,
                                                                                                  good_triplets_count,
                                                                                                  percentage))
        return percentage > self.source_config['closure']['percentage_of_good_triplets']
