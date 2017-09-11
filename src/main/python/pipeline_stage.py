import datetime
from logger import logger
from terminal_color import Color
from configs import config
from casa.flag_reasons import BAD_ANTENNA
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource
from sources.continuum_source import ContinuumSource
from sources.line_source import LineSource
from configs import pipeline_config


class PipelineStage(object):
    STAGE_TOGGLES = pipeline_config.STAGES_TOGGLE_CONFIG
    TARGET_SOURCE_STAGES = config.TARGET_SOURCE_CONFIGS['target_source_stages']
    CALIBRATION_STAGES = config.ALL_CONFIGS['calibration_stages']

    def __init__(self, measurement_set):
        self._measurement_set = measurement_set

    def _run(toggle_status):
        def toggle_decorator(stage_func):
            def stage_func_wrapper(*args):
                if toggle_status:
                    start_time = datetime.datetime.now()
                    stage_func(*args)
                    end_time = datetime.datetime.now()
                    logger.info(Color.LightCyan + Color.UNDERLINE + 'Time spent in ' + stage_func.__name__ + '= ' + str(
                        abs((end_time - start_time).seconds)) + " seconds" + Color.ENDC)

            return stage_func_wrapper
        return toggle_decorator

    @_run(STAGE_TOGGLES['flag_known_bad_data'])
    def flag_known_bad_antennas(self):
        self._measurement_set.quack()
        if pipeline_config.PIPELINE_CONFIGS['known_bad_data']:
            flag_file = "{0}/known_flags.txt".format(self._measurement_set.output_path)
            self._measurement_set.casa_runner.flagdata(flag_file, BAD_ANTENNA)

    @_run(STAGE_TOGGLES['flux_calibration'])
    def flux_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(self._measurement_set)
        flux_calibrator.run_setjy()
        if PipelineStage.CALIBRATION_STAGES['flux_calibration']['flagging']:
            flux_calibrator.reduce_data()
        else:
            flux_calibrator.calibrate()

    @_run(STAGE_TOGGLES['bandpass_calibration'])
    def bandpass_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(self._measurement_set)
        bandpass_calibrator.calibrate()
        if PipelineStage.CALIBRATION_STAGES['bandpass_calibration']['run_auto_flagging']:
            bandpass_calibrator.run_tfcrop()
            bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()

    @_run(STAGE_TOGGLES['phase_calibration'])
    def phase_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(self._measurement_set)
        phase_calibrator.calibrate()
        if PipelineStage.CALIBRATION_STAGES['phase_calibration']['flagging']:
            phase_calibrator.reduce_data()
        else:
            phase_calibrator.calibrate()

    @_run(STAGE_TOGGLES['target_source'])
    def target_source(self):
        for source_id in config.GLOBAL_CONFIG['target_src_field']:
            logger.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
            target_source = TargetSource(self._measurement_set, source_id)
            if self.TARGET_SOURCE_STAGES['calibrate']:
                target_source.calibrate()
            line_source = LineSource(target_source.line(), source_id)
            self._create_ref_continuum_image(line_source, source_id)
            self._run_autoflagging_on_line(line_source)
            self._create_all_spw_continuum_image(line_source, source_id)
            self._create_line_image(line_source)

    @_run(TARGET_SOURCE_STAGES['reference_spw']['create_continuum'])
    def _create_ref_continuum_image(self, line_source, source_id):
        cont_mode = 'ref'
        continuum_source_ref = ContinuumSource(
            line_source.continuum(config.GLOBAL_CONFIG['default_spw'], cont_mode),
            source_id, cont_mode)
        continuum_source_ref.reduce_data()
        line_source.extend_continuum_flags()
        if PipelineStage.TARGET_SOURCE_STAGES['reference_spw']['self_calibration']:
            continuum_source_ref.self_calibrate(cont_mode)


    @_run(TARGET_SOURCE_STAGES['all_spw']['run_auto_flagging'])
    def _run_autoflagging_on_line(self, line_source):
        line_source.run_tfcrop()
        line_source.run_rflag()

    @_run(TARGET_SOURCE_STAGES['all_spw']['create_continuum'])
    def _create_all_spw_continuum_image(self, line_source, source_id):
        if not self._is_single_spw_present():
            cont_mode = 'spw'
            spw_range = config.GLOBAL_CONFIG['spw_range']
            continuum_source = ContinuumSource(
                line_source.continuum(spw_range, cont_mode),
                source_id, cont_mode, spw_range)
            if PipelineStage.TARGET_SOURCE_STAGES['all_spw']['self_calibration']:
                continuum_source.self_calibrate(cont_mode)
        else:
            logger.info(
                Color.HEADER + 'Spw continuum image is already created [spw range contains only one spw]' + Color.ENDC)

    @_run(TARGET_SOURCE_STAGES['all_spw']['create_line_image'])
    def _create_line_image(self, line_source):
        cont_mode = 'ref' if self._is_single_spw_present() else 'spw'
        line_source.apply_calibration(cont_mode)
        line_source.create_line_image()

    def _is_single_spw_present(self):
        return config.GLOBAL_CONFIG['spw_range'].find(",") == -1