from configs.config import GLOBAL_CONFIG
from itertools import product
from src.main.python.analysers.analyser import Analyser
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from models.antenna_status import AntennaStatus
from analysers.analyser import Analyser
from analysers.r_matrix import RMatrix
import numpy
from models.phase_set import PhaseSet


class AngularDispersion(Analyser):
    def __init__(self, measurement_set, source):
        super(AngularDispersion, self).__init__(measurement_set, source)

    def identify_antennas_status(self):
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_config['field'])

        for polarization, scan_id in product(polarizations, scan_ids):
            base_antenna = self.measurement_set.get_antennas(polarization, scan_id)[0]
            r_matrix = RMatrix(polarization, scan_id)
            history = set()
            self._mark_antennas_status(polarization, scan_id, self.source_config, base_antenna, r_matrix, history)

    def _mark_antennas_status(self, polarization, scan_id, source_config, base_antenna, r_matrix, history):
        channel = source_config['channel']
        r_threshold = source_config['r_threshold']
        number_of_antennas = self.measurement_set.antenna_count()

        min_doubtful_antennas = int((source_config['percentage_threshold_for_min_doubtful_antennas']
                                     * number_of_antennas) / 100)
        good_antennas_threshold = int((source_config['percentage_threshold_for_good_antenna']
                                       * number_of_antennas) / 100)

        if base_antenna in history: return set()

        baselines = self.measurement_set.baselines_for(base_antenna, polarization, scan_id)
        data = self.measurement_set.get_data({'start': channel}, polarization,
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

        if len(doubtful_antennas) <= good_antennas_threshold:  # 70% is good
            for doubtful_antenna in doubtful_antennas:
                doubtful_antenna.update_state(polarization, scan_id, AntennaStatus.DOUBTFUL)
            base_antenna.update_state(polarization, scan_id, AntennaStatus.GOOD)

        else:
            doubtful_antennas = r_matrix.get_any_antennas(base_antenna, min_doubtful_antennas)
            base_antenna.update_state(polarization, scan_id, AntennaStatus.BAD)

        history.add(base_antenna)

        for doubtful_antenna in doubtful_antennas:
            self._mark_antennas_status(polarization, scan_id, source_config,
                                       doubtful_antenna, r_matrix, history)
