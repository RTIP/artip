import logging
from models.baseline import Baseline
from helpers import *
from configs.config import DETAIL_FLAG_CONFIG
from astropy.stats import median_absolute_deviation
import numpy
from terminal_color import Color


class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, channel, matrix={}):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._scan_id = scan_id
        self._channel = channel
        self.amplitude_data_matrix = self._generate_matrix() if measurement_set else matrix

    def _generate_matrix(self):
        antennaids = self._measurement_set.unflagged_antennaids(self._polarization, self._scan_id)
        amplitude_data_matrix = {}

        # TODO remove duplicate baselines
        for antenna1 in antennaids:
            for antenna2 in antennaids:
                if antenna1 < antenna2:
                    primary_antenna = antenna1
                    secondary_antenna = antenna2
                else:
                    primary_antenna = antenna2
                    secondary_antenna = antenna1

                if primary_antenna == secondary_antenna: continue

                filters = {
                    'antenna1': primary_antenna,
                    'antenna2': secondary_antenna,
                    'scan_number': self._scan_id
                }

                data = self._measurement_set.get_data({'start': self._channel}, self._polarization,
                                                      filters, ['corrected_amplitude', 'flag'])

                amplitude_data = self._mask_flagged_data_with_nan(data)

                baseline = Baseline(primary_antenna, secondary_antenna)
                amplitude_data_matrix[baseline] = amplitude_data
        return amplitude_data_matrix

    def _mask_flagged_data_with_nan(self, data):
        amplitude_data = data['corrected_amplitude'][0][0]
        flagged_rows = data['flag'][0][0]
        for idx, amp in enumerate(amplitude_data):
            if flagged_rows[idx]:
                amplitude_data[idx] = numpy.nan
        return amplitude_data

    def filter_by_antenna(self, antenna_id):
        antenna_matrix = dict((baseline, amp_data) for baseline, amp_data in self.amplitude_data_matrix.iteritems() if
                              baseline.contains(antenna_id))

        return AmplitudeMatrix(None, None, None, None, antenna_matrix)

    def filter_by_time(self, time_index):
        time_matrix = map(lambda baseline_amp: baseline_amp[time_index], self.amplitude_data_matrix.values())
        return AmplitudeMatrix(None, None, None, None,
                               {time_index: time_matrix})

    def filter_by_baseline(self, baseline):
        return AmplitudeMatrix(None, None, None, None,
                               {baseline: self.amplitude_data_matrix[baseline]})

    def readings_count(self):
        return len(self.amplitude_data_matrix[list(self.amplitude_data_matrix)[0]])

    def median(self):
        if is_nan(self.amplitude_data_matrix.values()): return numpy.nan
        return calculate_median(self.amplitude_data_matrix.values())

    def mad(self):
        if is_nan(self.amplitude_data_matrix.values()): return numpy.nan
        matrix = self.amplitude_data_matrix.values()
        return numpy.nanmedian(abs(numpy.array(matrix) - numpy.nanmedian(matrix)))

    def is_empty(self):
        return len(numpy.array(self.amplitude_data_matrix.values()).flatten()) == 0

    def is_bad(self, global_median, global_mad):
        matrix_median = self.median()
        matrix_mad = self.mad()
        if numpy.isnan(matrix_median) or numpy.isnan(matrix_mad): return False

        deviated_median = self._deviated_median(global_median, global_mad, matrix_median)
        scattered_amplitude = self._scattered_amplitude(global_mad, matrix_mad)
        if deviated_median or scattered_amplitude:
            logging.debug(Color.UNDERLINE + "matrix median=" + str(matrix_median) + ", matrix mad=" + str(
                    matrix_mad) + Color.ENDC)
            logging.debug(Color.WARNING + "median deviated=" + str(deviated_median) + ", amplitude scattered=" + str(
                    scattered_amplitude) + Color.ENDC)
        return deviated_median or scattered_amplitude

    def _deviated_median(self, global_median, global_mad, actual_median):
        return abs(actual_median - global_median) > (DETAIL_FLAG_CONFIG['mad_scale_factor'] * global_mad)

    def _scattered_amplitude(self, global_mad, actual_mad):
        return actual_mad > (DETAIL_FLAG_CONFIG['mad_scale_factor'] * global_mad)
