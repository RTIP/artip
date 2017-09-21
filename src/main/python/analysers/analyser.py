from configs import config

class Analyser(object):
    def __init__(self, measurement_set, source):
        self.measurement_set = measurement_set
        self.source_config = config.CALIBRATION_CONFIGS[source.source_type]
        self.source_ids = source.source_ids

    def identify_antennas_status(self):
        raise NotImplementedError("Not implemented")
