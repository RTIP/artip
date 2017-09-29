import datetime
from logger import logger
from terminal_color import Color
from configs import config
from casa.flag_reasons import BAD_ANTENNA
from sources.flux_calibrator import FluxCalibrator
from sources.bandpass_calibrator import BandpassCalibrator
from sources.phase_calibrator import PhaseCalibrator
from sources.target_source import TargetSource


class PipelineStage(object):
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

    @_run(config.MAIN_STAGES['flag_known_bad_data'])
    def flag_known_bad_antennas(self):
        self._measurement_set.quack()
        if config.MAIN_STAGES['flag_known_bad_data']:
            flag_file = "{0}/user_defined_flags.txt".format(config.CONFIG_PATH)
            self._measurement_set.casa_runner.flagdata(flag_file)
        self._measurement_set.generate_flag_summary("known_flags")

    @_run(config.MAIN_STAGES['flux_calibration'])
    def flux_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Flux Calibration" + Color.ENDC)
        flux_calibrator = FluxCalibrator(self._measurement_set)
        flux_calibrator.run_setjy()
        if config.CALIBRATION_STAGES['flux_calibration']['flagging']:
            flux_calibrator.reduce_data()
        else:
            flux_calibrator.calibrate()

    @_run(config.MAIN_STAGES['bandpass_calibration'])
    def bandpass_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Bandpass Calibration" + Color.ENDC)
        bandpass_calibrator = BandpassCalibrator(self._measurement_set)
        bandpass_calibrator.calibrate()
        if config.CALIBRATION_STAGES['bandpass_calibration']['run_auto_flagging']:
            bandpass_calibrator.run_tfcrop()
            bandpass_calibrator.run_rflag()
        bandpass_calibrator.calibrate()

    @_run(config.MAIN_STAGES['phase_calibration'])
    def phase_calibration(self):
        logger.info(Color.SOURCE_HEADING + "Phase Calibration" + Color.ENDC)
        phase_calibrator = PhaseCalibrator(self._measurement_set)
        phase_calibrator.calibrate()
        if config.CALIBRATION_STAGES['phase_calibration']['flagging']:
            phase_calibrator.reduce_data()
        else:
            phase_calibrator.calibrate()

    def target_source(self):
        if self._target_source_toggle():
            for source_id in config.GLOBAL_CONFIGS['target_src_fields']:
                logger.info(Color.SOURCE_HEADING + "Target Source Calibration" + Color.ENDC)
                target_source = TargetSource(self._measurement_set, source_id)
                if config.TARGET_SOURCE_STAGES['calibrate']:
                    target_source.calibrate()
                line = target_source.line()
                line.measurement_set.generate_flag_summary("known_flags")
                self._create_ref_continuum_image(line)
                self._run_autoflagging_on_line(line)
                self._create_all_spw_continuum_image(line)
                self._create_line_image(line)

    @_run(config.MAIN_STAGES['target_source']['ref_continuum'])
    def _create_ref_continuum_image(self, line_source):
        cont_mode = 'ref'
        continuum_source_ref = line_source.continuum(config.GLOBAL_CONFIGS['default_spw'], cont_mode)
        if config.TARGET_SOURCE_STAGES['ref_continuum']['flagging']:
            continuum_source_ref.reduce_data()
        if config.TARGET_SOURCE_STAGES['ref_continuum']['extend_flags']:
            line_source.extend_continuum_flags()
        if config.TARGET_SOURCE_STAGES['ref_continuum']['image']:
            continuum_source_ref.base_image()
        if config.TARGET_SOURCE_STAGES['ref_continuum']['selfcal']:
            continuum_source_ref.self_calibrate(cont_mode)

    def _run_autoflagging_on_line(self, line_source):
        if self._run_autoflagging_toggle():
            line_source.run_tfcrop()
            line_source.run_rflag()

    @_run(config.MAIN_STAGES['target_source']['all_spw_continuum'])
    def _create_all_spw_continuum_image(self, line_source):
        if not self._is_single_spw_present():
            cont_mode = 'spw'
            spw_range = config.GLOBAL_CONFIGS['spw_range']
            continuum_source = line_source.continuum(spw_range, cont_mode)
            if config.TARGET_SOURCE_STAGES['all_spw']['continuum']['selfcal']:
                continuum_source.base_image()
                continuum_source.self_calibrate(cont_mode)
        else:
            logger.info(
                Color.HEADER + 'Spw continuum image is already created [spw range contains only one spw]' + Color.ENDC)

    @_run(config.MAIN_STAGES['target_source']['all_spw_line'])
    def _create_line_image(self, line_source):
        cont_mode = 'ref' if self._is_single_spw_present() else 'spw'
        if config.TARGET_SOURCE_STAGES['all_spw']['line']['apply_selfcal']:
            line_source.apply_calibration(cont_mode)
        if config.TARGET_SOURCE_STAGES['all_spw']['line']['image']:
            line_source.create_line_image()

    def _is_single_spw_present(self):
        return config.GLOBAL_CONFIGS['spw_range'].find(",") == -1

    def _target_source_toggle(self):
        return config.MAIN_STAGES['target_source']['ref_continuum'] or \
               config.MAIN_STAGES['target_source']['all_spw_continuum'] or \
               config.MAIN_STAGES['target_source']['all_spw_line']

    def _run_autoflagging_toggle(self):
        return (config.MAIN_STAGES['target_source']['all_spw_continuum'] or
                config.MAIN_STAGES['target_source']['all_spw_line']) and \
               config.TARGET_SOURCE_STAGES['all_spw']['run_auto_flagging']
