from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from sources.source import Source


class BandpassCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'bandpass_calibrator'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['bandpass_cal_field']
        super(BandpassCalibrator, self).__init__(measurement_set)

    def calibrate(self):
        self.measurement_set.casa_runner.apply_bandpass_calibration(self.config)
