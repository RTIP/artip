from logger import logger
import numpy
from terminal_color import Color
from named_tuples import CalibParams

class AmplitudeMatrix:
    def __init__(self, measurement_set, polarization, scan_id, spw, config, matrix={}):
        self._measurement_set = measurement_set
        self._polarization = polarization
        self._spw = spw
        self._scan_id = scan_id
        self._config = config
        self.amplitude_data_matrix = self._generate_matrix() if measurement_set else matrix

    def _generate_matrix(self):
        baselines = self._measurement_set.baselines(self._polarization, self._scan_id)
        amplitude_data_matrix = {}
        matrix_data = self._matrix_data()

        for baseline in baselines:
            baseline_index = matrix_data.baseline_index((baseline.antenna1, baseline.antenna2))
            if not numpy.isnan(baseline_index):
                amplitude_data_matrix[baseline] = matrix_data.mask_baseline_data(baseline_index)
        return amplitude_data_matrix

    def _matrix_data(self):
        calib_params = CalibParams(*self._config['calib_params'])
        amplitude_data_column = self._config['detail_flagging']['amplitude_data_column']
        visibility_data = self._measurement_set.get_data(self._spw, {'start': calib_params.channel,
                                                                     'width': calib_params.width},
                                                         self._polarization, {'scan_number': self._scan_id},
                                                         ["antenna1", "antenna2", amplitude_data_column, 'flag',
                                                          'time'])
        return visibility_data

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

    def count_non_nan(self):
        data = numpy.array(self.amplitude_data_matrix.values()).flatten()
        return numpy.isfinite(data).sum()

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

    def has_sufficient_data(self, window_config):
        threshold = window_config.bucket_size - window_config.overlap
        return self.count_non_nan() > threshold

    def is_bad(self, global_median, deviation_threshold):
        matrix_median = self.median()
        matrix_sigma = self.mad_sigma()

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

    def __repr__(self):
        return "AmpMatrix=" + str(self.amplitude_data_matrix) + " med=" + \
               str(self.median()) + " mad sigma=" + str(self.mad_sigma())
