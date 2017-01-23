from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from sources.source import Source


class BandpassCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'bandpass_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['bandpass_cal_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(BandpassCalibrator, self).__init__(measurement_set, self.source_name)

    def calibrate(self):
        CasaRunner.apply_bandpass_calibration(self.config)
