import logging

from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS
from configs.debugging_config import DEBUG_CONFIGS
from flaggers.detailed_flagger import DetailedFlagger
from report import Report
from sources.source import Source
from src.main.python.analysers.closure_phases import ClosureAnalyser
from src.main.python.analysers.angular_dispersion import AngularDispersion
from terminal_color import Color


class FluxCalibrator(Source):
    def __init__(self, measurement_set):
        super(FluxCalibrator, self).__init__(measurement_set, 'flux_calibration')

    def flag_and_calibrate(self):
        if not DEBUG_CONFIGS['manual_flag']:
            logging.info(
                Color.HEADER + "Identifying bad Antennas based on angular dispersion in phases...\n" + Color.ENDC)
            r_analyser = AngularDispersion(self.measurement_set, self.source_name)
            r_analyser.identify_antennas_status()

            logging.info(Color.HEADER + "Identifying bad Antennas based closure phases...\n" + Color.ENDC)
            closure_analyser = ClosureAnalyser(self.measurement_set, self.source_name)
            closure_analyser.identify_antennas_status()

            scan_ids = self.measurement_set.scan_ids_for(ALL_CONFIGS[self.source_name]['field'])
            Report(self.measurement_set.antennas).generate_report(scan_ids)

            logging.info(Color.HEADER + "Flagging R and Closure based bad antennas..." + Color.ENDC)
            self.measurement_set.flag_r_and_closure_based_bad_antennas()

            logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
            CasaRunner.apply_flux_calibration()
            logging.info(Color.HEADER + "Flux Calibration Applied..." + Color.ENDC)

        logging.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
        detailed_flagger = DetailedFlagger(self.measurement_set)
        detailed_flagger.get_bad_antennas('flux_calibration')
