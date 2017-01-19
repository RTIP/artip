import datetime
import logging
from configs.config import DATASET
from sources.flux_calibrator import FluxCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from terminal_color import Color


def main():
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(DATASET)

    flux_calibrator = FluxCalibrator(measurement_set)
    flux_calibrator.run_setjy()
    flux_calibrator.reduce_data()
    flux_calibrator.run_rflag()
    flux_calibrator.run_bandpass()

    phase_calibrator = PhaseCalibrator(measurement_set)
    phase_calibrator.calibrate()
    phase_calibrator.reduce_data()

    target_source = TargetSource(measurement_set)
    target_source.reduce_data()

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)
