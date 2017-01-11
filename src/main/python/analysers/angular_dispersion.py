from itertools import product
from src.main.python.analysers.analyser import Analyser
from src.main.python.flaggers.r_matrix import RMatrix
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from models.antenna_status import AntennaStatus


class AngularDispersion(Analyser):
    def __init__(self, measurement_set, source):
        super(AngularDispersion, self).__init__(measurement_set, source)

    def identify_antennas_status(self):
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_config['field'])
        base_antenna = self.measurement_set.antennas[0]

        for polarization, scan_id in product(polarizations, scan_ids):
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

        baselines = self.measurement_set.baselines_for(base_antenna)
        for (antenna1, antenna2) in baselines:
            # TODO: dont calculate again if present in r-matrix
            filter_params = {'scan_number': scan_id, 'antenna1': antenna1.id, 'antenna2': antenna2.id}
            phase_set = self.measurement_set.get_phase_data({'start': channel}, polarization, filter_params)
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
