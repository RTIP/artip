from configs.config import ALL_CONFIGS

class Analyser(object):
    def __init__(self, measurement_set, source):
        self.measurement_set = measurement_set
        self.source_config = ALL_CONFIGS[source]

    def identify_antennas_status(self):
        raise NotImplementedError("Not implemented")
