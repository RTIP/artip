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
    def __init__(self, measurement_set, source_name):
        self.source_name = source_name
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
        self.flag_antennas_in_detail()
        self.flag_baselines_in_detail()

    def flag_antennas_in_detail(self):
        debugger = Debugger(self.measurement_set)
        detailed_analyser = DetailedAnalyser(self.measurement_set)
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_id)
        polarization_scan_product = list(itertools.product(polarizations, scan_ids))

        while True:
            bad_antenna_present = detailed_analyser.analyse_antennas(polarization_scan_product, self.config, debugger)
            if bad_antenna_present:
                logging.info(Color.HEADER + 'Flagging Bad Antenna Time in CASA' + Color.ENDC)
                self.measurement_set.casa_runner.flagdata(BAD_ANTENNA_TIME)
                self.calibrate()
            else:
                logging.info(Color.OKGREEN + 'No Bad Antennas were Found' + Color.ENDC)
                break

    def flag_baselines_in_detail(self):
        debugger = Debugger(self.measurement_set)
        detailed_analyser = DetailedAnalyser(self.measurement_set)
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_id)
        polarization_scan_product = list(itertools.product(polarizations, scan_ids))

        while True:
            bad_baseline_present = detailed_analyser.analyse_baselines(polarization_scan_product, self.config,
                                                                       debugger)
            if bad_baseline_present:
                logging.info(Color.HEADER + 'Flagging Bad Baselines Time in CASA' + Color.ENDC)
                self.measurement_set.casa_runner.flagdata(BAD_BASELINE_TIME)
                self.calibrate()
            else:
                logging.info(Color.OKGREEN + 'No Bad Baselines were Found' + Color.ENDC)
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
