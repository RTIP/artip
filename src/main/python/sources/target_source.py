from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from sources.source import Source


class TargetSource(Source):
    def __init__(self, measurement_set):
        self.source_type = 'target_source'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['target_src_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(TargetSource, self).__init__(measurement_set, self.source_name)

    def flag_antennas(self):
        return True

    def calibrate(self):
        CasaRunner.apply_target_source_calibration(self.source_id)
