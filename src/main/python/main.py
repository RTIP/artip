import logging
from configs.config import FLUX_CAL_CONFIG, DATASET
from configs.debugging_config import DEBUG_CONFIGS
from casa.flag_reasons import BAD_ANTENNA
from flaggers.closure_flagger import ClosureFlagger
from flaggers.r_flagger import RFlagger
from measurement_set import MeasurementSet
from flaggers.detailed_flagger import DetailedFlagger
from report import Report
from terminal_color import Color
from casa.casa_runner import CasaRunner


def main():
    measurement_set = MeasurementSet(DATASET)
    if not DEBUG_CONFIGS['manual_flag']:
        logging.info(Color.HEADER + "Identifying bad Antennas based on angular dispersion in phases...\n" + Color.ENDC)
        r_flagger = RFlagger(measurement_set)
        r_flagger.get_bad_baselines('flux_calibration')
        logging.info(Color.HEADER + "Identifying bad Antennas based closure phases...\n" + Color.ENDC)
        closure_flagger = ClosureFlagger(measurement_set)
        closure_flagger.get_bad_baselines()
        scan_ids = measurement_set.scan_ids_for(FLUX_CAL_CONFIG['field'])
        Report(measurement_set.antennas).generate_report(scan_ids)
        logging.info(Color.HEADER + "Flagging R and Closure based bad antennas..." + Color.ENDC)
        measurement_set.flag_r_and_closure_based_bad_antennas()
        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        CasaRunner.apply_flux_calibration()
        logging.info(Color.HEADER + "Flux Calibration Applied..." + Color.ENDC)
    logging.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
    detailed_flagger = DetailedFlagger(measurement_set)
    detailed_flagger.get_bad_antennas('flux_calibration')