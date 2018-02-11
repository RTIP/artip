from artip.sources.source import Source
from artip.configs import config

class BandpassCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'bandpass_calibrator'
        self.config = config.CALIBRATION_CONFIGS[self.source_type]
        self.source_ids = config.GLOBAL_CONFIGS['bandpass_cal_fields']
        super(BandpassCalibrator, self).__init__(measurement_set)

    def calibrate(self):
        self.measurement_set.casa_runner.apply_bandpass_calibration(self.config)
        self.measurement_set.casa_runner.apply_flux_calibration(self.config, 2)
