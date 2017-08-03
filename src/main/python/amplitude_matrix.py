from logger import logger
import numpy
from terminal_color import Color
from helpers import minus
from collections import namedtuple


class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, spw, config, matrix={}):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._spw = spw
        self._scan_id = scan_id
        self._config = config
        self.amplitude_data_matrix = self._generate_matrix() if measurement_set else matrix

    def _generate_matrix(self):
        all_times = self._measurement_set.timesforscan(self._scan_id, False)
        baselines = self._measurement_set.baselines(self._polarization, self._scan_id)
        amplitude_data_matrix = {}
        data = self._matrix_data()

        for baseline in baselines:
            amplitude_data = numpy.array([])
            baseline_amp_times = numpy.array([])
            baseline_indices = numpy.logical_and(data.antenna1_list == baseline.antenna1,
                                                 data.antenna2_list == baseline.antenna2).nonzero()[0]
            for index in baseline_indices:
                baseline_amp_times = numpy.append(baseline_amp_times, data.times[index])
                if data.flags[index]:
                    amplitude_data = numpy.append(amplitude_data, numpy.nan)
                else:
                    amplitude_data = numpy.append(amplitude_data, data.amplitudes[index])

            amplitude_data_matrix[baseline] = self._sanitize_baseline_data(amplitude_data, baseline_amp_times,
                                                                           all_times)
        return amplitude_data_matrix

    def _matrix_data(self):
        MatrixData = namedtuple('Data', 'amplitudes antenna1_list antenna2_list flags times')
        amplitude_data_column = self._config['detail_flagging']['amplitude_data_column']
        data = self._measurement_set.get_data(self._spw,
                                              {'start': self._config['channel'], 'width': self._config['width']},
                                              self._polarization,
                                              {'scan_number': self._scan_id},
                                              ["antenna1", "antenna2", amplitude_data_column, 'flag', 'time'])
        return MatrixData(data[amplitude_data_column][0][0], data['antenna1'], data['antenna2'], data['flag'][0][0],
                          data['time'])

    def filter_by_antenna(self, antenna_id):
        antenna_matrix = dict((baseline, amp_data) for baseline, amp_data in self.amplitude_data_matrix.iteritems() if
                              baseline.contains(antenna_id))

        return AmplitudeMatrix(None, None, None, None, self._config, antenna_matrix)

    def filter_by_baseline(self, baseline):
        return AmplitudeMatrix(None, None, None, None, self._config,
                               {baseline: self.amplitude_data_matrix[baseline]})

    def readings_count(self):
        return len(self.amplitude_data_matrix[list(self.amplitude_data_matrix)[0]])

    def is_nan(self):
        return all(numpy.isnan(amp) for amp in numpy.array(self.amplitude_data_matrix.values()).flatten())

    def median(self):
        if self.is_nan(): return numpy.nan
        return numpy.nanmedian(self.amplitude_data_matrix.values())

    def mad(self):
        if self.is_nan(): return numpy.nan
        matrix = self.amplitude_data_matrix.values()
        return numpy.nanmedian(abs(numpy.array(matrix) - numpy.nanmedian(matrix)))

    def mad_sigma(self):
        return 1.4826 * self.mad()

    def mean(self):
        if self.is_nan(): return numpy.nan
        return numpy.nanmean(self.amplitude_data_matrix.values())

    def mean_sigma(self):
        if self.is_nan(): return numpy.nan
        return numpy.nanstd(self.amplitude_data_matrix.values())

    def is_empty(self):
        return len(numpy.array(self.amplitude_data_matrix.values()).flatten()) == 0

    def is_bad(self, global_median, deviation_threshold):
        matrix_median = self.median()
        matrix_sigma = self.mad_sigma()
        if numpy.isnan(matrix_median) or numpy.isnan(matrix_sigma): return False

        deviated_median = self._deviated_median(global_median, deviation_threshold, matrix_median)
        scattered_amplitude = self._scattered_amplitude(deviation_threshold, matrix_sigma)
        if deviated_median or scattered_amplitude:
            logger.debug(Color.UNDERLINE + "matrix=" + str(self.amplitude_data_matrix) + Color.ENDC)
            logger.debug(Color.UNDERLINE + " median=" + str(matrix_median) + ", median sigma=" + str(matrix_sigma)
                         + ", mean=" + str(self.mean()) + ", mean sigma=" + str(self.mean_sigma()) + Color.ENDC)
            logger.debug(Color.WARNING + "median deviated=" + str(deviated_median) + ", amplitude scattered=" + str(
                scattered_amplitude) + Color.ENDC)
        return deviated_median or scattered_amplitude

    def _deviated_median(self, global_median, deviation_threshold, actual_median):
        return abs(actual_median - global_median) > deviation_threshold

    def _scattered_amplitude(self, deviation_threshold, actual_sigma):
        return actual_sigma > deviation_threshold

    def _sanitize_baseline_data(self, baseline_amp, baseline_amp_times, all_times):
        if len(baseline_amp) < len(all_times):
            missing_indices = self._missing_time_indices(baseline_amp_times, all_times)
            for index in missing_indices:
                baseline_amp = numpy.insert(baseline_amp, index, numpy.nan)
        return baseline_amp

    def _missing_time_indices(self, baseline_amp_times, all_times):
        missing_times = minus(all_times, baseline_amp_times)
        return map(lambda missing_time: numpy.where(all_times == missing_time)[0][0], missing_times)

    def __repr__(self):
        return "AmpMatrix=" + str(self.amplitude_data_matrix) + " med=" + \
               str(self.median()) + " mad sigma=" + str(self.mad_sigma())
