import datetime
from logger import logger
from configs import pipeline_config
from configs import config
from measurement_set import MeasurementSet
from terminal_color import Color
from pipeline_stage import PipelineStage


def main(dataset_path):
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(dataset_path, config.OUTPUT_PATH)
    measurement_set.quack()

    pipeline_stages = PipelineStage(measurement_set)

    if pipeline_config.STAGES_CONFIG['flux_calibration']:
        pipeline_stages.flux_calibration()

    if pipeline_config.STAGES_CONFIG['bandpass_calibration']:
        pipeline_stages.bandpass_calibration()

    if pipeline_config.STAGES_CONFIG['phase_calibration']:
        pipeline_stages.phase_calibration()

    if run_target_source(pipeline_config.STAGES_CONFIG['target_source']):
        pipeline_stages.target_source()

    end_time = datetime.datetime.now()
    logger.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)


def run_target_source(target_source_exec_steps):
    return target_source_exec_steps['all_spw']['create_line_image'] or target_source_exec_steps['all_spw'][
        'create_continuum'] or target_source_exec_steps['all_spw']['run_auto_flagging'] or \
           target_source_exec_steps['reference_spw']['create_continuum']
