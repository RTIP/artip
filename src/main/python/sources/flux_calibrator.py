import logging

from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS,GLOBAL_CONFIG
from configs.debugging_config import DEBUG_CONFIGS
from report import Report
from sources.source import Source
from terminal_color import Color
from models.antenna_status import AntennaStatus


class FluxCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'flux_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['flux_cal_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(FluxCalibrator, self).__init__(measurement_set, self.source_name)

    def run_setjy(self):
        CasaRunner.setjy(self.source_id, self.source_name)

    def run_bandpass(self):
        logging.info(Color.HEADER + "Running Bandpass Calibration..." + Color.ENDC)
        CasaRunner.apply_bandpass_calibration()

    def flag_antennas(self):
        if not DEBUG_CONFIGS['manual_flag']:
            self.analyse_antennas_on_angular_dispersion()
            self.analyse_antennas_on_closure_phases()

            scan_ids = self.measurement_set.scan_ids_for(self.source_id)
            Report(self.measurement_set.antennas).generate_report(scan_ids)

            logging.info(Color.HEADER + "Flagging R and Closure based bad antennas..." + Color.ENDC)

            def is_bad(state):
                return state.get_R_phase_status() == AntennaStatus.BAD and state.get_closure_phase_status() == AntennaStatus.BAD

            self.measurement_set.flag_bad_antennas(is_bad)

    def calibrate(self):
        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        CasaRunner.apply_flux_calibration()
        logging.info(Color.HEADER + "Flux Calibration Applied..." + Color.ENDC)