class Flagger(object):
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_baselines(self):
        raise NotImplementedError("Not implemented")
