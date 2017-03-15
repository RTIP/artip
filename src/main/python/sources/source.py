import itertools
import logging
from analysers.angular_dispersion import AngularDispersion
from analysers.closure_analyser import ClosureAnalyser
from analysers.detailed_analyser import DetailedAnalyser
from casa.flag_reasons import BAD_ANTENNA_TIME, BAD_BASELINE_TIME
from configs.config import GLOBAL_CONFIG
from configs.pipeline_config import PIPELINE_CONFIGS
from helpers import Debugger
from terminal_color import Color


class Source(object):
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def run_rflag(self):
        self.measurement_set.casa_runner.r_flag(self.source_type)

    def calibrate(self):
        raise NotImplementedError("Not implemented")

    def reduce_data(self):
        if not PIPELINE_CONFIGS['manual_flag']: self.flag_antennas()
        self.calibrate()
        self.flag_and_calibrate_in_detail()

    def flag_and_calibrate_in_detail(self):
        logging.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
        detailed_analyser = DetailedAnalyser(self.measurement_set, self.config)
        self._flag_bad_time(BAD_ANTENNA_TIME, detailed_analyser.analyse_antennas)
        self._flag_bad_time(BAD_BASELINE_TIME, detailed_analyser.analyse_baselines)

    def _flag_bad_time(self, reason, analyser):
        debugger = Debugger(self.measurement_set)
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_ids)
        polarization_scan_product = list(itertools.product(polarizations, scan_ids))
        while True:
            bad_time_present = analyser(polarization_scan_product, debugger)
            if bad_time_present:
                logging.info(Color.HEADER + 'Flagging {0} in CASA'.format(reason) + Color.ENDC)
                self.measurement_set.casa_runner.flagdata(reason)
                self.calibrate()
            else:
                logging.info(Color.OKGREEN + 'No {0} Found'.format(reason) + Color.ENDC)
                break

    def analyse_antennas_on_closure_phases(self):
        logging.info(Color.HEADER + "Identifying bad Antennas based on closure phases..." + Color.ENDC)
        closure_analyser = ClosureAnalyser(self.measurement_set, self.source_type)
        closure_analyser.identify_antennas_status()

    def analyse_antennas_on_angular_dispersion(self):
        logging.info(
            Color.HEADER + "Identifying bad Antennas based on angular dispersion in phases..." + Color.ENDC)
        r_analyser = AngularDispersion(self.measurement_set, self.source_type)
        r_analyser.identify_antennas_status()
