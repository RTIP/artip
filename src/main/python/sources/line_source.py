from sources.target_source import TargetSource
from configs import config


class LineSource(TargetSource):
    def __init__(self, measurement_set):
        super(LineSource, self).__init__(measurement_set)
        self.source_type = 'line'
        self.config = config.ALL_CONFIGS["target_source"][self.source_type]

    def apply_calibration(self):
        self.measurement_set.casa_runner.apply_line_calibration(self.config["calmode"])

    def reduce_data(self):
        self.measurement_set.casa_runner.extend_continuum_flags()

    def create_line_image(self):
        self.measurement_set.casa_runner.create_line_image(self.config['image'])
