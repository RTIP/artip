class Source(object):
    def __init__(self, measurement_set, source_name):
        self.source_name = source_name
        self.measurement_set = measurement_set

    def flag_and_calibrate(self):
        raise NotImplementedError("Should have implemented this")
