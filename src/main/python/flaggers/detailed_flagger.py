import itertools
from helpers import *
from helpers import Debugger as debugger
from config import *
from amplitude_matrix import AmplitudeMatrix
from astropy.stats import median_absolute_deviation
from debugging_config import DEBUG_CONFIGS

class DetailedFlagger:
    def __init__(self, measurement_set):
        self.measurement_set = measurement_set

    def get_bad_antennas(self, source):
        antenna_deviation = time_deviation = baseline_deviation = {}
        polarizations = GLOBAL_CONFIG['polarizations']
        source_config = ALL_CONFIGS[source]
        scan_ids = self.measurement_set.scan_ids_for(source_config['field'])

        for polarization, scan_id in itertools.product(polarizations, scan_ids):
            amp_matrix = AmplitudeMatrix(self.measurement_set, polarization, scan_id, source_config['channel'])

            if DEBUG_CONFIGS['manual_flag']: debugger().filter_matrix(amp_matrix.amplitude_data_matrix)

            ideal_median = calculate_median(amp_matrix.amplitude_data_matrix.values())
            ideal_mad = median_absolute_deviation(amp_matrix.amplitude_data_matrix.values())
            print '**********************'

            # print polarization, ' ', scan_id
            print "Ideal values =>", ideal_median, " =>", ideal_mad

            unflagged_antennaids = self.measurement_set.unflagged_antennaids(polarization, scan_id)
            for antenna_id in unflagged_antennaids:
                antenna_matrix = amp_matrix.filter_by_antenna(antenna_id)
                if len(antenna_matrix.keys()) > 0:
                    antenna_median = calculate_median(antenna_matrix.values())
                    antenna_mad = median_absolute_deviation(antenna_matrix.values())
                    antenna_deviation[antenna_id] = abs(ideal_median - antenna_median)
            antenna_median_deviation = calculate_median(antenna_deviation.values())
            for antenna_id in antenna_deviation:
                deviation_ratio = (antenna_deviation[antenna_id] / antenna_median_deviation)
                if deviation_ratio > 5:
                    print "Bad Antenna=", antenna_id
                elif deviation_ratio > 3:
                    print "Border line Antenna=", antenna_id
            print '**********************'

            time_snapshots_count = len(amp_matrix.amplitude_data_matrix[list(amp_matrix.amplitude_data_matrix)[0]])
            for index in range(0, time_snapshots_count, 1):
                time_amps = map(lambda baseline_amp: baseline_amp[index], amp_matrix.amplitude_data_matrix.values())
                timeline_median = calculate_median(time_amps)
                timeline_mad = median_absolute_deviation(time_amps)
                time_deviation[index] = abs(ideal_median - timeline_median)
                # print timeline_median, ',', abs(ideal_median - timeline_median)
            time_median_deviation = calculate_median(time_deviation.values())
            for time_index in time_deviation:
                deviation_ratio = (time_deviation[time_index] / time_median_deviation)
                if deviation_ratio > 5:
                    print "Bad Time=", time_index
                elif deviation_ratio > 3:
                    print "Border line Time=", time_index
            print '**********************'

            for base_lines, amplitudes in amp_matrix.amplitude_data_matrix.items():
                baseline_median = calculate_median(amplitudes)
                baseline_mad = median_absolute_deviation(amplitudes)
                baseline_deviation[base_lines] = abs(ideal_median - baseline_median)
            baseline_median_deviation = calculate_median(baseline_deviation.values())

            for baseline in baseline_deviation:
                deviation_ratio = (baseline_deviation[baseline] / baseline_median_deviation)
                if deviation_ratio > 5:
                    print "Bad Baseline=", baseline
                elif deviation_ratio > 3:
                    print "Border line Baseline=", baseline
            print '**********************'