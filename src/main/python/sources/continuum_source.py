from configs import config
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from terminal_color import Color
import itertools
from logger import logger


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set, source_id, cont_mode, spw='0'):
        super(ContinuumSource, self).__init__(measurement_set, source_id)
        self.source_type = 'continuum'
        self.spw = spw
        self.source_ids = [0]  # source_id will always be 0
        self.config = config.ALL_CONFIGS["target_source"][self.source_type]
        self.cont_mode = cont_mode

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def _flag_bad_time(self, reason, analyser):
        polarizations = config.GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_ids)
        spw_polarization_scan_product = list(itertools.product(self.spw, polarizations, scan_ids))
        self.analyse_and_flag_once(reason, analyser, spw_polarization_scan_product)

    def self_calibrate(self, mode):
        config = self.config['self_calibration']
        self._base_image()
        self_caled_p = self.apply_self_calibration(config, 'p', mode)
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
        self.measurement_set.casa_runner.base_image(self.config['image'])

    def _source_name(self):
        continuum_source_id = 0  # Will be always 0
        return self.measurement_set.get_field_name_for(continuum_source_id)
