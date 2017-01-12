import logging

from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS
from configs.debugging_config import DEBUG_CONFIGS
from report import Report
from sources.source import Source
from src.main.python.analysers.closure_phases import ClosureAnalyser
from src.main.python.analysers.angular_dispersion import AngularDispersion
from terminal_color import Color


class FluxCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'flux_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = self.config['field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(FluxCalibrator, self).__init__(measurement_set, self.source_name)

    def run_setjy(self):
        CasaRunner.setjy(self.source_id, self.source_name)

    def _flag_antennas(self):
        if not DEBUG_CONFIGS['manual_flag']:
            self._analyse_on_angular_dispersion()
            self._analyse_on_closure_phases()

            scan_ids = self.measurement_set.scan_ids_for(self.source_id)
            Report(self.measurement_set.antennas).generate_report(scan_ids)

            logging.info(Color.HEADER + "Flagging R and Closure based bad antennas..." + Color.ENDC)
            self.measurement_set.flag_r_and_closure_based_bad_antennas()

    def reduce_data(self):
        self._flag_antennas()
        self.calibrate()
        self._flag_and_calibrate_in_detail()

    def _flag_and_calibrate_in_detail(self):
        logging.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
        self.flag_antennas_in_detail()
        self.flag_baselines_in_detail()

    def calibrate(self):
        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        CasaRunner.apply_flux_calibration()
        logging.info(Color.HEADER + "Flux Calibration Applied..." + Color.ENDC)

    def _analyse_on_closure_phases(self):
        logging.info(Color.HEADER + "Identifying bad Antennas based closure phases...\n" + Color.ENDC)
        closure_analyser = ClosureAnalyser(self.measurement_set, self.source_type)
        closure_analyser.identify_antennas_status()

    def _analyse_on_angular_dispersion(self):
        logging.info(
                Color.HEADER + "Identifying bad Antennas based on angular dispersion in phases...\n" + Color.ENDC)
        r_analyser = AngularDispersion(self.measurement_set, self.source_type)
        r_analyser.identify_antennas_status()
