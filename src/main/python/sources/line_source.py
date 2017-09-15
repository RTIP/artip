from sources.target_source import TargetSource
from configs import config


class LineSource(TargetSource):
    def __init__(self, measurement_set, source_id):
        super(LineSource, self).__init__(measurement_set, source_id)
        self.source_type = 'line'
        self.source_ids = [0]  # source_id will always be 0
        self.config = config.ALL_CONFIGS["target_source"][self.source_type]

    def apply_calibration(self, mode):
        self.measurement_set.casa_runner.apply_line_calibration(self.config["calmode"], self.source_id, mode)
        self.measurement_set.reload()

    def extend_continuum_flags(self):
        self.measurement_set.casa_runner.extend_continuum_flags(self.source_id)
        scan_ids = self.measurement_set.scan_ids(self.source_ids)
        self.measurement_set.casa_runner.generate_flag_summary("detailed_flagging", scan_ids, self.source_type)

    def create_line_image(self):
        self.measurement_set.casa_runner.create_line_image(self.config["calmode"], self.source_id)
