from config import *
from flaggers.closure_flagger import ClosureFlagger
from flaggers.r_flagger import RFlagger
from measurement_set import MeasurementSet
from report import Report


def main(ms_dataset):
    measurement_set = MeasurementSet(ms_dataset)
    print "Calculating bad baselines based on angular dispersion in phases..."
    r_flagger = RFlagger(measurement_set)
    r_flagger.get_bad_baselines('flux_calibration')
    print "Calculating bad baselines based closure phases..."
    closure_flagger = ClosureFlagger(measurement_set)
    closure_flagger.get_bad_baselines()
    scan_ids = measurement_set.scan_ids_for(FLUX_CAL_CONFIG['field'])
    Report(measurement_set.antennas).generate_report(scan_ids)

    # r_flagger.optimized_r_based_bad_baselines('flux_calibration')
