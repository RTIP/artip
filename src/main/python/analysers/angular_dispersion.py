from configs import config
from logger import logger
from itertools import product, imap
from models.antenna_status import AntennaStatus
from analysers.analyser import Analyser
from analysers.r_matrix import RMatrix
import numpy
from models.phase_set import PhaseSet
from terminal_color import Color


class AngularDispersion(Analyser):
    def __init__(self, measurement_set, source):
        super(AngularDispersion, self).__init__(measurement_set, source)

    def identify_antennas_status(self):
        spw_polarization_scan_id_combination = []
        spw = config.GLOBAL_CONFIG['default_spw']

        for polarization in config.GLOBAL_CONFIG['polarizations']:
            scan_ids = self.measurement_set.scan_ids(self.source_config['fields'], polarization)
            spw_polarization_scan_id_combination += list(product(spw, [polarization], scan_ids))

        for spw, polarization, scan_id in spw_polarization_scan_id_combination:
            logger.debug(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
            if config.GLOBAL_CONFIG['refant']:
                base_antenna = self.measurement_set.get_antenna_by_id(config.GLOBAL_CONFIG['refant'])
            else:
                base_antenna = self.measurement_set.antennas(polarization, scan_id)[0]
            r_matrix = RMatrix(spw, polarization, scan_id)
            history = set()
            antenna_count = self.measurement_set.antenna_count(polarization, scan_id)
            self._mark_antennas_status(spw, polarization, scan_id, self.source_config, base_antenna, r_matrix, history,
                                       antenna_count)

            logger.debug("Percentage of antennas analysed={0}".format(len(history) * 100 / antenna_count))

    def _mark_antennas_status(self, spw, polarization, scan_id, source_config, base_antenna, r_matrix, history,
                              antenna_count):
        channel = source_config['channel']
        width = source_config['width']
        r_threshold = source_config['angular_dispersion']['r_threshold']
        if base_antenna in history: return

        data = self.measurement_set.get_data(spw, {'start': channel, 'width': width}, polarization,
                                             {'scan_number': scan_id},
                                             ["antenna1", "antenna2", 'phase', 'flag'], True)
        antenna1_list = data['antenna1']
        antenna2_list = data['antenna2']
        phase_list = data['phase'][0][0]
        flags = data['flag'][0][0]
        baselines = self.measurement_set.baselines_for(base_antenna, polarization, scan_id)

        baselines_count = len(baselines)
        good_baselines_threshold = int((source_config['angular_dispersion']['percentage_of_good_antennas']
                                        * baselines_count) / 100)
        min_doubtful_antennas = int((source_config['angular_dispersion']['percentage_of_min_doubtful_antennas']
                                     * baselines_count) / 100)

        for (antenna1, antenna2) in baselines:
            if not self._phase_data_present_for_baseline((antenna1.id, antenna2.id), data):
                baselines_count -= 1
                continue

            baseline_index = numpy.logical_and(antenna1_list == antenna1.id,
                                                 antenna2_list == antenna2.id).nonzero()[0][0]

            phase_data = self._mask_flagged_data(phase_list[baseline_index], flags[baseline_index])

            phase_set = PhaseSet(phase_data)
            r_value = phase_set.calculate_angular_dispersion()
            if r_value == PhaseSet.INVALID_ANGULAR_DISPERSION:
                baselines_count -= 1

            another_antenna = antenna2 if base_antenna == antenna1 else antenna1
            r_matrix.add(base_antenna, another_antenna, r_value)

        doubtful_antennas = r_matrix.get_doubtful_antennas(base_antenna, r_threshold, min_doubtful_antennas)

        good_baselines_count = baselines_count - len(doubtful_antennas)
        if good_baselines_count >= good_baselines_threshold:
            for doubtful_antenna in doubtful_antennas:
                doubtful_antenna.update_state(polarization, scan_id, AntennaStatus.DOUBTFUL)
            base_antenna.update_state(polarization, scan_id, AntennaStatus.GOOD)
        else:
            doubtful_antennas = set()
            base_antenna.update_state(polarization, scan_id, AntennaStatus.BAD)

        history.add(base_antenna)

        if baselines_count == 0:
            logger.debug("Antenna={0} was flagged".format(base_antenna))
        else:
            logger.debug("Antenna={0}, total_baselines={1}, good_baselines_count={2}, Percentage={3}".format(
                base_antenna, baselines_count, good_baselines_count,
                good_baselines_count * 100 / baselines_count))

        for doubtful_antenna in doubtful_antennas:
            self._mark_antennas_status(spw, polarization, scan_id, source_config,
                                       doubtful_antenna, r_matrix, history, antenna_count)

    def _phase_data_present_for_baseline(self, baseline, data):
        baseline = tuple(sorted(baseline))
        baseline_index_in_phase_data = \
            numpy.logical_and(data['antenna1'] == baseline[0], data['antenna2'] == baseline[1]).nonzero()[0]
        return bool(baseline_index_in_phase_data.shape[0])

    def _mask_flagged_data(self, baseline_phases, flags):
        return list(imap(lambda phase, flag: numpy.nan if flag else phase, baseline_phases, flags))