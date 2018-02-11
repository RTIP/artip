import datetime

from configs import config
from pipeline_stage import PipelineStage
from models.measurement_set import MeasurementSet
from utilities.logger import logger
from utilities.terminal_color import Color


def main(dataset_path):
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(dataset_path, config.OUTPUT_PATH)

    pipeline_stages = PipelineStage(measurement_set)
    pipeline_stages.flag_known_bad_antennas()
    pipeline_stages.flux_calibration()
    pipeline_stages.bandpass_calibration()
    pipeline_stages.phase_calibration()
    pipeline_stages.target_source()

    end_time = datetime.datetime.now()
    logger.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)