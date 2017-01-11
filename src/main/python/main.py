import datetime
import logging

from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS, DATASET
from configs.debugging_config import DEBUG_CONFIGS
from flaggers.detailed_flagger import DetailedFlagger
from measurement_set import MeasurementSet
from report import Report
from src.main.python.analysers.closure_phases import ClosureAnalyser
from src.main.python.analysers.angular_dispersion import AngularDispersion
from terminal_color import Color


def main():
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(DATASET)
    measurement_set.run_setjy()
    source = 'flux_calibration'
    if not DEBUG_CONFIGS['manual_flag']:
        logging.info(Color.HEADER + "Identifying bad Antennas based on angular dispersion in phases...\n" + Color.ENDC)
        r_analyser = AngularDispersion(measurement_set, source)
        r_analyser.identify_antennas_status()

        logging.info(Color.HEADER + "Identifying bad Antennas based closure phases...\n" + Color.ENDC)
        closure_analyser = ClosureAnalyser(measurement_set, source)
        closure_analyser.identify_antennas_status()

        scan_ids = measurement_set.scan_ids_for(ALL_CONFIGS[source]['field'])
        Report(measurement_set.antennas).generate_report(scan_ids)

        logging.info(Color.HEADER + "Flagging R and Closure based bad antennas..." + Color.ENDC)
        measurement_set.flag_r_and_closure_based_bad_antennas()

        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        CasaRunner.apply_flux_calibration()
        logging.info(Color.HEADER + "Flux Calibration Applied..." + Color.ENDC)

    logging.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
    detailed_flagger = DetailedFlagger(measurement_set)
    detailed_flagger.get_bad_antennas('flux_calibration')
    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)
