import itertools
from helpers import *
from config import *
from amplitude_matrix import AmplitudeMatrix
from astropy.stats import median_absolute_deviation


class DetailedFlagger:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_antennas(self, source):
        antenna_deviation = {}
        # deviation = []
        polarizations = GLOBAL_CONFIG['polarizations']
        source_config = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_config['field'])

        for polarization, scan_id in itertools.product(polarizations, scan_ids):
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])
            ideal_median = calculate_median(amp_matrix.amplitude_data_matrix.values())
            ideal_mad = median_absolute_deviation(amp_matrix.amplitude_data_matrix.values())
            print '**********************'
            print polarization,' ',scan_id
            print "Ideal values =>", ideal_median, " =>", ideal_mad

            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)
            # print "Antennas===", unflagged_antennaids
            for antenna_id in unflagged_antennaids:
                antenna_matrix = amp_matrix.filter_by_antenna(antenna_id)
                antenna_median = calculate_median(antenna_matrix.values())
                antenna_mad = median_absolute_deviation(antenna_matrix.values())
                antenna_deviation[antenna_id] = abs(ideal_median - antenna_median)
                # deviation.append(ideal_median - antenna_median)
                # print antenna_id, ',', antenna_median, ',', antenna_mad
            median_deviation = calculate_median(antenna_deviation.values())
            for antenna_id in antenna_deviation:
                deviation_ratio = (antenna_deviation[antenna_id] / median_deviation)
                if deviation_ratio > 5:
                    print "Bad=", antenna_id
                elif deviation_ratio > 3:
                    print "Border line=", antenna_id
            print '**********************'