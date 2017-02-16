from sources.target_source import TargetSource


class LineSource(TargetSource):
    def __init__(self, measurement_set):
        super(LineSource, self).__init__(measurement_set)
