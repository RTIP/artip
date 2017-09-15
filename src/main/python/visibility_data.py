import re
import numpy
from itertools import imap


class VisibilityData:
    DATA_COLUMN_IN_RAW_DATA = ['corrected_phase', 'corrected_amplitude', 'phase', 'amplitude']
    FLAG_COLUMN_IN_RAW_DATA = ['flag']

    def __init__(self, raw_data):
        for key, value in raw_data.iteritems():
            key, value = self._sanatize_input_data(key, value)
            setattr(self, key, value)

    def _sanatize_input_data(self, key, value):
        if key in VisibilityData.DATA_COLUMN_IN_RAW_DATA:
            key = 'data'
            value = value[0][0]
        if key in VisibilityData.FLAG_COLUMN_IN_RAW_DATA:
            value = value[0][0]
        return key, value

    def baseline_index(self, baseline):
        baseline_index = numpy.logical_and(self.antenna1 == baseline[0], self.antenna2 == baseline[1]).nonzero()[0]
        return baseline_index[0] if baseline_index.size else numpy.nan

    def mask_baseline_data(self, baseline_index, mask_with=numpy.nan):
        baseline_data = self.data[baseline_index]
        baseline_flags = self.flag[baseline_index]
        return list(imap(lambda amplitude, flag: mask_with if flag else amplitude, baseline_data, baseline_flags))

    def phase_data_present_for_baseline(self, baseline):
        baseline = tuple(sorted(baseline))
        return True if self.baseline_index(baseline) else False

    def phase_data_present_for_triplet(self, triplet):
        triplet_baselines_flag_status = {}
        baseline_combinations = [(triplet[0].id, triplet[1].id),
                                 (triplet[1].id, triplet[2].id),
                                 (triplet[0].id, triplet[2].id)]

        for baseline in baseline_combinations:
            triplet_baselines_flag_status[baseline] = self._flags_status_for(baseline)

        return self._is_triplet_flagged(triplet_baselines_flag_status)

    def _is_triplet_flagged(self, triplet_baselines_flag_status):
        return not all(sum(triplet_baselines_flag_status.values()))

    def _flags_status_for(self, baseline):
        baseline = tuple(sorted(baseline))
        if not self.phase_data_present_for_baseline(baseline): return True
        baseline_index = self.baseline_index(baseline)
        phase_data_flags_status = self.flag[baseline_index]
        return phase_data_flags_status
