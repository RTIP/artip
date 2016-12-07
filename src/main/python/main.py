from measurement_set import MeasurementSet

from flaggers.r_flagger import RFlagger
from flaggers.closure_flagger import ClosureFlagger


def main(ms_dataset):
    measurement_set = MeasurementSet(ms_dataset)
    print "Calculating bad baselines based on angular dispersion in phases..."
    r_flagger = RFlagger(measurement_set)
    print r_flagger.get_bad_baselines()
    print "Calculating bad baselines based closure phases..."
    closure_flagger = ClosureFlagger(measurement_set)
    closure_flagger.get_bad_baselines()
