from unittest import TestCase
from config import *
from flagger import Flagger
from mock import Mock, mock, call
from phase_set import PhaseSet

from baseline import Baseline


class FlaggerTest(TestCase):

    @mock.patch('config.GLOBAL_CONFIG', GLOBAL_CONFIG.update({'polarizations': ['RR']}))
    def setUp(self):
        self.mocked_ms = Mock(name="ms")
        self.dispersed_phase_set = Mock(name='dispersed_phase_set', spec=PhaseSet)
        self.non_dispersed_phase_set = Mock(name='non_dispersed_phase_set', spec=PhaseSet)
        self.dispersed_phase_set.is_dispersed.return_value = True
        self.non_dispersed_phase_set.is_dispersed.return_value = False

    def test_get_bad_baselines_should_return_bad_baselines(self):
        flagger = Flagger(self.mocked_ms)

        self.mocked_ms.scan_ids_for.return_value = [1]
        self.mocked_ms.baselines.return_value = [(0, 1), (0, 2)]
        self.mocked_ms.get_phase_data.side_effect = [self.dispersed_phase_set, self.non_dispersed_phase_set]

        actual_bad_baselines = flagger.get_bad_baselines()

        filter_params1 = {'primary_filters': {'polarization': 'RR', 'channel': FLUX_CAL_CONFIG['channel']},
                         'extra_filters': {'scan_number': 1, 'antenna1': 0, 'antenna2': 1}}

        filter_params2 = {'primary_filters': {'polarization': 'RR', 'channel': FLUX_CAL_CONFIG['channel']},
                         'extra_filters': {'scan_number': 1, 'antenna1': 0, 'antenna2': 2}}

        expected = [call.get_phase_data(filter_params1),call.get_phase_data(filter_params2)]

        self.mocked_ms.assert_has_calls(expected, any_order=True)

        self.mocked_ms.scan_ids_for.assert_called_with(FLUX_CAL_CONFIG['field'])
        self.dispersed_phase_set.is_dispersed.assert_called_with(FLUX_CAL_CONFIG['r_threshold'])
        self.non_dispersed_phase_set.is_dispersed.assert_called_with(FLUX_CAL_CONFIG['r_threshold'])
        expected_bad_baselines = [Baseline(0, 1, 'RR', 1)]
        self.assertItemsEqual(expected_bad_baselines, actual_bad_baselines)