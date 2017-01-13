import logging

from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS
from configs.debugging_config import DEBUG_CONFIGS
from report import Report
from sources.source import Source
from terminal_color import Color
from models.antenna_status import AntennaStatus


class PhaseCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'phase_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = self.config['field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(PhaseCalibrator, self).__init__(measurement_set, self.source_name)

    def flag_antennas(self):
        if not DEBUG_CONFIGS['manual_flag']:
            self.analyse_antennas_on_closure_phases()
            scan_ids = self.measurement_set.scan_ids_for(self.source_id)
            Report(self.measurement_set.antennas).generate_report(scan_ids)

            def is_bad(state):
                return state.get_closure_phase_status() == AntennaStatus.BAD

            self.measurement_set.flag_bad_antennas(is_bad)

    def calibrate(self):
        CasaRunner.apply_phase_calibration()
