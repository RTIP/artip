import datetime
from logger import logger
from terminal_color import Color
from configs import config
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from sources.continuum_source import ContinuumSource
from sources.line_source import LineSource
from configs import pipeline_config


class PipelineStage(object):
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def _log_timing(stage_func):
        def stage_func_wrapper(*args):
            start_time = datetime.datetime.now()
            stage_func(*args)
            end_time = datetime.datetime.now()
            logger.info(Color.LightCyan + Color.UNDERLINE + 'Time spent in ' + stage_func.__name__ + '= ' + str(
                abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)

        return stage_func_wrapper

    @_log_timing
    def flux_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(self.measurement_set)
        flux_calibrator.run_setjy()
        flux_calibrator.reduce_data()

    @_log_timing
    def bandpass_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(self.measurement_set)
        bandpass_calibrator.calibrate()
        bandpass_calibrator.run_tfcrop()
        bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()

    @_log_timing
    def phase_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(self.measurement_set)
        phase_calibrator.calibrate()
        phase_calibrator.reduce_data()

    @_log_timing
    def target_source(self):
        target_source_exec_steps = pipeline_config.STAGES_CONFIG['target_source']
        for source_id in config.GLOBAL_CONFIG['target_src_field']:
            logger.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
            target_source = TargetSource(self.measurement_set, source_id)
            target_source.calibrate()
            line_source = LineSource(target_source.line(), source_id)

            if target_source_exec_steps['reference_spw']['create_continuum']:
                cont_mode = 'ref'
                continuum_source_ref = ContinuumSource(
                    line_source.continuum(config.GLOBAL_CONFIG['default_spw'], cont_mode),
                    source_id, cont_mode)
                continuum_source_ref.reduce_data()
                continuum_source_ref.self_calibrate(cont_mode)
                line_source.extend_continuum_flags()

            if target_source_exec_steps['all_spw']['run_auto_flagging']:
                line_source.run_tfcrop()
                line_source.run_rflag()

            cont_mode = 'spw'
            if target_source_exec_steps['all_spw']['create_continuum']:
                spw_range = config.GLOBAL_CONFIG['spw_range']
                continuum_source = ContinuumSource(
                    line_source.continuum(spw_range, cont_mode),
                    source_id, cont_mode, spw_range)
                continuum_source.self_calibrate(cont_mode)

            if target_source_exec_steps['all_spw']['create_line_image']:
                line_source.apply_calibration(cont_mode)
                line_source.create_line_image()
