from sources.target_source import TargetSource
from configs import config


class LineSource(TargetSource):
    def __init__(self, measurement_set, source_id):
        super(LineSource, self).__init__(measurement_set, source_id)
        self.source_type = 'line'
        self.config = config.ALL_CONFIGS["target_source"][self.source_type]

    def apply_calibration(self):
        self.measurement_set.casa_runner.apply_line_calibration(self.config["calmode"], self.source_id)
        self.measurement_set.reload()

    def reduce_data(self):
        self.measurement_set.casa_runner.extend_continuum_flags(self.source_id)

    def create_line_image(self):
        self.measurement_set.casa_runner.create_line_image(self.config['image'])
