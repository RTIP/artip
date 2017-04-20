import datetime
import logging
from configs import pipeline_config
from configs import config
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from terminal_color import Color
from sources.continuum_source import ContinuumSource
from sources.line_source import LineSource
from casa.flag_recorder import FlagRecorder


def main(dataset_path):
    start_time = datetime.datetime.now()
    measurement_set = MeasurementSet(dataset_path, config.OUTPUT_PATH)
    measurement_set.quack()
    if pipeline_config.STAGES_CONFIG['flux_calibration']:
        logging.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(measurement_set)
        flux_calibrator.run_setjy()
        flux_calibrator.reduce_data()

    if pipeline_config.STAGES_CONFIG['bandpass_calibration']:
        logging.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(measurement_set)
        bandpass_calibrator.calibrate()
        bandpass_calibrator.run_tfcrop()
        bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()
    if pipeline_config.STAGES_CONFIG['phase_calibration']:
        logging.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(measurement_set)
        phase_calibrator.calibrate()
        phase_calibrator.reduce_data()

    target_source_exec_steps = pipeline_config.STAGES_CONFIG['target_source']
    if run_target_source(target_source_exec_steps):
        logging.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
        target_source = TargetSource(measurement_set)
        target_source.calibrate()
        line_source = LineSource(target_source.line())
        if target_source_exec_steps['run_auto_flagging']:
            line_source.run_tfcrop()
            line_source.run_rflag()
        if target_source_exec_steps['create_continuum']:
            continuum_source = ContinuumSource(line_source.continuum())
            continuum_source.reduce_data()
            continuum_source.self_calibrate()
            line_source.reduce_data()
        if target_source_exec_steps['create_line_image']:
            line_source.apply_calibration()
            line_source.create_line_image()

    end_time = datetime.datetime.now()
    logging.info(Color.UNDERLINE + 'Total time =' + str(abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)


def run_target_source(target_source_exec_steps):
    return target_source_exec_steps['create_line_image'] or target_source_exec_steps['create_continuum'] or \
           target_source_exec_steps['run_auto_flagging']
