from sources.target_source import TargetSource


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set):
        super(ContinuumSource, self).__init__(measurement_set)
