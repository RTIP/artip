from measurement_set import MeasurementSet
from flagger import Flagger


def main(ms_dataset):
    measurement_set = MeasurementSet(ms_dataset)
    print "Calculating bad baselines based on angular dispersion in phases..."
    flagger = Flagger(measurement_set)
    print flagger.get_bad_baselines()
    flagger.closure_based_bad_baselines()
