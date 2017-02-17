from configs.config import ALL_CONFIGS
from sources.target_source import TargetSource


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set):
        super(ContinuumSource, self).__init__(measurement_set)
        self.source_type = 'continuum'
        self.config = ALL_CONFIGS["target_source"][self.source_type]

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def self_calibrate(self):
        self._base_image()
        self.measurement_set.casa_runner.apply_self_calibration(self.config['self_calibration'])

    def _base_image(self):
        self.measurement_set.casa_runner.base_image(self.config['image'])
