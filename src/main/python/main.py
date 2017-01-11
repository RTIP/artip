import datetime
import logging
from configs.config import DATASET
from sources.flux_calibrator import FluxCalibrator
from measurement_set import MeasurementSet
from terminal_color import Color


def main():
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(DATASET)

    flux_calibrator = FluxCalibrator(measurement_set)
    flux_calibrator.run_setjy()
    sources = [flux_calibrator]

    for source in sources:
        source.flag_and_calibrate()

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)
