from configs import config
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from casa.flag_reasons import BAD_ANTENNA, BAD_ANTENNA_TIME, BAD_BASELINE_TIME, BAD_TIME
from analysers.detailed_analyser import DetailedAnalyser
from terminal_color import Color
from logger import logger


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set, source_id, cont_mode, spw='0'):
        super(ContinuumSource, self).__init__(measurement_set, source_id)
        self.source_type = 'continuum'
        self.flag_file = "{0}/flags_{1}.txt".format(measurement_set.output_path, self.source_type)
        self.spw = spw
        self.source_ids = [0]
        self.config = config.TARGET_SOURCE_CONFIGS[self.source_type]
        self.cont_mode = cont_mode

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def calibrate(self):
        pass

    def flag_and_calibrate_in_detail(self):
        logger.info(Color.HEADER + "Started Detail Flagging..." + Color.ENDC)
        detailed_analyser = DetailedAnalyser(self.measurement_set, self.config, self.flag_file)
        self._flag_bad_time(BAD_TIME, detailed_analyser.analyse_time, True)
        self._flag_bad_time(BAD_ANTENNA_TIME, detailed_analyser.analyse_antennas, True)
        self._flag_bad_time(BAD_BASELINE_TIME, detailed_analyser.analyse_baselines, True)

    def self_calibrate(self, mode):
        config = self.config['self_calibration']
        self._base_image()
        cal_mode = config['calmode']
        p_loop_count = cal_mode['p']['loop_count']
        ap_loop_count = cal_mode['ap']['loop_count']

        if p_loop_count is not 0:
            self_caled_p = self.apply_self_calibration(config, 'p', mode)

        if p_loop_count is 0 and ap_loop_count is not 0:
            self.apply_self_calibration(config, 'ap', mode)

        if p_loop_count is not 0 and ap_loop_count is not 0:
            self_caled_p.attach_model(config, 'p')
            self_caled_p.apply_self_calibration(config, 'ap', mode)

    def apply_self_calibration(self, config, cal_mode, mode):
        ms_path, output_path = self.prepare_output_dir("self_caled_{0}_{1}_{2}".format(cal_mode, mode, self.source_id))
        self.measurement_set.casa_runner.apply_self_calibration(config, cal_mode, ms_path, output_path,
                                                                self.spw)
        return ContinuumSource(MeasurementSet(ms_path, output_path), self.source_id, mode, self.spw)

    def attach_model(self, self_calibration_config, cal_mode):
        self.measurement_set.casa_runner.fourier_transform(self._source_name(), cal_mode,
                                                           self.spw,
                                                           self_calibration_config['calmode'][cal_mode]['loop_count'])

    def _base_image(self):
        self.measurement_set.casa_runner.base_image()

    def _source_name(self):
        continuum_source_id = 0  # Will be always 0
        return self.measurement_set.get_field_name_for(continuum_source_id)
