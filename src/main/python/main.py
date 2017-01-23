import datetime
import logging
from configs.pipeline_config import STAGES_CONFIG
from configs.config import DATASET_PATH
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from terminal_color import Color


def main():
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(DATASET_PATH)

    if STAGES_CONFIG['flux_calibration']:
        logging.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(measurement_set)
        flux_calibrator.run_setjy()
        flux_calibrator.reduce_data()

    if STAGES_CONFIG['bandpass_calibration']:
        logging.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(measurement_set)
        bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()

    if STAGES_CONFIG['phase_calibration']:
        logging.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(measurement_set)
        phase_calibrator.calibrate()
        phase_calibrator.reduce_data()

    if STAGES_CONFIG['target_source']:
        logging.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
        target_source = TargetSource(measurement_set)
        target_source.reduce_data()

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)
