import itertools
from helpers import *
from config import *
from amplitude_matrix import AmplitudeMatrix
# from astropy.stats import median_absolute_deviation


class DetailedFlagger:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_antennas(self, source):
        polarizations = GLOBAL_CONFIG['polarizations']
        source_config = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_config['field'])

        for polarization, scan_id in itertools.product(polarizations, scan_ids):
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])
            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)
            for antenna_id in unflagged_antennaids:
                antenna_matrix = amp_matrix.filter_by_antenna(antenna_id)
                print antenna_id, ' = ', calculate_median(antenna_matrix.values())
