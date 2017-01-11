import unittest
from configs.config import GLOBAL_CONFIG,FLUX_CAL_CONFIG
from mock import Mock, mock, call
from models.baseline import Baseline
from models.phase_set import PhaseSet
from unittest import TestCase

from src.main.python.analysers.angular_dispersion import AngularDispersion


class RFlaggerTest(TestCase):
    @mock.patch('config.GLOBAL_CONFIG', GLOBAL_CONFIG.update({'polarizations': ['RR']}))
    def setUp(self):
        self.mocked_ms = Mock(name="ms")
        self.dispersed_phase_set = Mock(name='dispersed_phase_set', spec=PhaseSet)
        self.non_dispersed_phase_set = Mock(name='non_dispersed_phase_set', spec=PhaseSet)
        self.dispersed_phase_set.is_dispersed.return_value = True
        self.non_dispersed_phase_set.is_dispersed.return_value = False


    @unittest.skip("Disabled")
    def test_get_bad_baselines_should_return_bad_baselines(self):
        flagger = AngularDispersion(self.mocked_ms)

        self.mocked_ms.scan_ids_for.return_value = [1]
        self.mocked_ms.baselines.return_value = [(0, 1), (0, 2)]
        self.mocked_ms.get_phase_data.side_effect = [self.dispersed_phase_set, self.non_dispersed_phase_set]

        actual_bad_baselines = flagger.identify_antennas_status()

        filter_params1 = {'scan_number': 1, 'antenna1': 0, 'antenna2': 1}
        filter_params2 = {'scan_number': 1, 'antenna1': 0, 'antenna2': 2}

        expected = [call.get_phase_data({'start': FLUX_CAL_CONFIG['channel']}, 'RR', filter_params1),
                    call.get_phase_data({'start': FLUX_CAL_CONFIG['channel']}, 'RR', filter_params2)]

        self.mocked_ms.assert_has_calls(expected, any_order=True)

        self.mocked_ms.scan_ids_for.assert_called_with(FLUX_CAL_CONFIG['field'])
        self.dispersed_phase_set.is_dispersed.assert_called_with(FLUX_CAL_CONFIG['r_threshold'])
        self.non_dispersed_phase_set.is_dispersed.assert_called_with(FLUX_CAL_CONFIG['r_threshold'])
        expected_bad_baselines = [Baseline(0, 1, 'RR', 1)]
        self.assertItemsEqual(expected_bad_baselines, actual_bad_baselines)
