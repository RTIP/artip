from configs.config import ALL_CONFIGS
from sources.target_source import TargetSource
from measurement_set import MeasurementSet


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set):
        super(ContinuumSource, self).__init__(measurement_set)
        self.source_type = 'continuum'
        self.config = ALL_CONFIGS["target_source"][self.source_type]

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def self_calibrate(self):
        config = self.config['self_calibration']
        self_caled_p = self.split_phase_cal(config, 'p')
        self_caled_p.attach_model(config, 'p')
        self_caled_p.split_amp_phase_cal(config, 'ap')

    def split_phase_cal(self, config, cal_mode):
        self._base_image()
        ms_path, output_path = self.prepare_output_dir("self_caled_p")
        self.measurement_set.casa_runner.apply_self_calibration(config, cal_mode, ms_path, output_path)
        return ContinuumSource(MeasurementSet(ms_path, output_path))

    def split_amp_phase_cal(self, config, cal_mode):
        ms_path, output_path = self.prepare_output_dir("self_caled_ap")
        self.measurement_set.casa_runner.apply_self_calibration(config, cal_mode, ms_path, output_path)
        return ContinuumSource(MeasurementSet(ms_path, output_path))

    def attach_model(self, self_calibration_config, cal_mode):
        self.measurement_set.casa_runner.fourier_transform(self._source_name(),
                                                           self._image_model(self_calibration_config, cal_mode))

    def _base_image(self):
        self.measurement_set.casa_runner.base_image(self.config['image'])

    def _source_name(self):
        continuum_source_id = 0  # Will be always 0
        return self.measurement_set.get_field_name_for(continuum_source_id)

    def _image_model(self, self_calibration_config, cal_mode):
        image_path = '{0}/self_cal_image'.format(self.measurement_set.get_output_path())
        return "{0}_{1}_{2}.model".format(image_path, cal_mode,
                                          self_calibration_config['calmode'][cal_mode]['loop_count'] - 1)
