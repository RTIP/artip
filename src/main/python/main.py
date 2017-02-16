import datetime
import logging
import os
from configs.pipeline_config import STAGES_CONFIG
from configs.config import OUTPUT_PATH
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from terminal_color import Color
from sources.continuum_source import ContinuumSource
from sources.line_source import LineSource


def main(dataset_path):
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(dataset_path, output_path(dataset_path))
    measurement_set.quack()

    if STAGES_CONFIG['flux_calibration']:
        logging.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(measurement_set)
        flux_calibrator.run_setjy()
        flux_calibrator.reduce_data()

    if STAGES_CONFIG['bandpass_calibration']:
        logging.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(measurement_set)
        # bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()

    if STAGES_CONFIG['phase_calibration']:
        logging.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(measurement_set)
        phase_calibrator.calibrate()
        phase_calibrator.reduce_data()

    if STAGES_CONFIG['target_source']:
        logging.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
        target_source = TargetSource(measurement_set)
        target_source.calibrate()
        line_source = LineSource(target_source.line())
        continuum_source = ContinuumSource(target_source.continuum())

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)


def output_path(dataset_path):
    dataset_name = os.path.splitext(os.path.basename(dataset_path))[0]
    ms_output_path = OUTPUT_PATH + "/" + dataset_name
    if not os.path.exists(ms_output_path):
        os.makedirs(ms_output_path)
    return ms_output_path
