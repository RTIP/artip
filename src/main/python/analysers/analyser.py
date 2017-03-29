from configs import config

class Analyser(object):
    def __init__(self, measurement_set, source):
        self.measurement_set = measurement_set
        self.source_config = config.ALL_CONFIGS[source]

    def identify_antennas_status(self):
        raise NotImplementedError("Not implemented")
