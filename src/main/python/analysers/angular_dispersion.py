from configs import config
import logging
from itertools import product
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
        polarizations = config.GLOBAL_CONFIG['polarizations']
        spws = config.GLOBAL_CONFIG['default_spw']
        scan_ids = self.measurement_set.scan_ids_for(self.source_config['fields'])
        for spw, polarization, scan_id in product(spws, polarizations, scan_ids):
            logging.debug(
                Color.BACKGROUD_WHITE + "Polarization =" + polarization + " Scan Id=" + str(scan_id) + Color.ENDC)
            if config.GLOBAL_CONFIG['refant']:
                base_antenna = self.measurement_set.get_antenna_by_id(config.GLOBAL_CONFIG['refant'])
            else:
                base_antenna = self.measurement_set.get_antennas(polarization, scan_id)[0]
            r_matrix = RMatrix(spw, polarization, scan_id)
            history = set()
            self._mark_antennas_status(spw, polarization, scan_id, self.source_config, base_antenna, r_matrix, history)

    def _mark_antennas_status(self, spw, polarization, scan_id, source_config, base_antenna, r_matrix, history):
        channel = source_config['channel']
        width = source_config['width']
        r_threshold = source_config['angular_dispersion']['r_threshold']
        number_of_antenna_pairs = self.measurement_set.antenna_count() - 1

        min_doubtful_antennas = int((source_config['angular_dispersion']['percentage_of_min_doubtful_antennas']
                                     * number_of_antenna_pairs) / 100)
        good_antennas_threshold = int((source_config['angular_dispersion']['percentage_of_good_antennas']
                                       * number_of_antenna_pairs) / 100)

        if base_antenna in history: return set()
        baselines = self.measurement_set.baselines_for(base_antenna, polarization, scan_id)
        data = self.measurement_set.get_data(spw, {'start': channel, 'width': width}, polarization,
                                             {'scan_number': scan_id},
                                             ["antenna1", "antenna2", 'phase'])
        antenna1_list = data['antenna1']
        antenna2_list = data['antenna2']
        phase_list = data['phase'][0][0]

        for (antenna1, antenna2) in baselines:
            # TODO: dont calculate again if present in r-matrix
            baseline_indexes = numpy.logical_and(antenna1_list == antenna1.id,
                                                 antenna2_list == antenna2.id).nonzero()[0]
            phase_data = numpy.array([])
            for index in baseline_indexes:
                phase_data = numpy.append(phase_data, phase_list[index])

            phase_set = PhaseSet(phase_data)
            r_value = phase_set.calculate_angular_dispersion()

            another_antenna = antenna2 if base_antenna == antenna1 else antenna1

            r_matrix.add(base_antenna, another_antenna, r_value)

        doubtful_antennas = r_matrix.get_doubtful_antennas(base_antenna, r_threshold, min_doubtful_antennas)
        logging.debug("Antenna={0}, History={1}, Doubtfuls={2}".format(base_antenna, history, doubtful_antennas))
        # print "~~~~~~",base_antenna.id
        # if base_antenna.id ==9: print r_matrix

        number_of_good__antenna_pairs = number_of_antenna_pairs - len(doubtful_antennas)
        if number_of_good__antenna_pairs >= good_antennas_threshold:
            for doubtful_antenna in doubtful_antennas:
                doubtful_antenna.update_state(polarization, scan_id, AntennaStatus.DOUBTFUL)
            base_antenna.update_state(polarization, scan_id, AntennaStatus.GOOD)

        else:
            doubtful_antennas = set()
            base_antenna.update_state(polarization, scan_id, AntennaStatus.BAD)
            logging.debug("Antenna={0}, Doubtfuls={1} Marked bad".format(base_antenna, doubtful_antennas))

        history.add(base_antenna)

        for doubtful_antenna in doubtful_antennas:
            self._mark_antennas_status(spw, polarization, scan_id, source_config,
                                       doubtful_antenna, r_matrix, history)
