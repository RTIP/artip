import datetime
import logging
from configs.config import DATASET
from sources.flux_calibrator import FluxCalibrator
from sources.phase_calibrator import PhaseCalibrator
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
    phase_calibrator.reduce_data()

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)
