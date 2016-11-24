from config import Config
from measurement_set import MeasurementSet
from flagger import Flagger

def main(ms_dataset):
    ms = MeasurementSet(ms_dataset)
    config=Config('./conf/config.yml')
    print "Calculating bad baselines based on angular dispersion in phases..."
    flagger = Flagger(ms,config)
    print flagger.get_bad_baselines('flux_calibration')