from unittest import TestCase
from measurement_set import MeasurementSet
from phase_set import PhaseSet
import mock
from mock import Mock
from mock import patch


class TestMeasurementSet(TestCase):

    @mock.patch('casac.casac')
    def setUp(self, mock_casac):
        self.casa_measurement_set = Mock()
        self.phase_set_data = {'phase': [[[-2.85, -1.2, 2.1, -2.3, -2.8]]]}
        mock_casac.ms.return_value = self.casa_measurement_set
        self.ms = MeasurementSet('ms_file_path')
        self.casa_measurement_set.open.assert_called_with("ms_file_path")
        self.casa_measurement_set.getdata.return_value = self.phase_set_data

    def test_get_phase_data_should_select_only_primary_filters(self):
        filter_params = {'primary_filters': {'polarization': 'RR'}}

        self.ms.get_phase_data(filter_params)

        self.casa_measurement_set.selectinit.assert_called_with(reset=True)
        self.casa_measurement_set.selectpolarization.assert_called_with('RR')
        self.casa_measurement_set.select.assert_not_called()

    def test_get_phase_data_should_select_extra_filters(self):
        filter_params = {'antenna1': 0, 'antenna2': 1}
        filters = {'extra_filters': filter_params}

        self.ms.get_phase_data(filters)

        self.casa_measurement_set.selectinit.assert_called_with(reset=True)
        self.casa_measurement_set.selectpolarization.assert_not_called()
        self.casa_measurement_set.select.assert_called_with(filter_params)

    def test_get_phase_data_should_select_both_filters(self):
        filter_params = {'antenna1': 0, 'antenna2': 1}
        filters = {'primary_filters': {'polarization': 'RR', 'channel': 100}, 'extra_filters': filter_params}

        self.ms.get_phase_data(filters)

        self.casa_measurement_set.selectinit.assert_called_with(reset=True)
        self.casa_measurement_set.selectpolarization.assert_called_with('RR')
        self.casa_measurement_set.selectchannel.assert_called_with(100)
        self.casa_measurement_set.select.assert_called_with(filter_params)

    @mock.patch("phase_set.PhaseSet.__init__")
    def test_get_phase_data_should_return_PhaseSet_instance(self, phase_set_init):
        phase_set_init.return_value = None
        filter_params = {'primary_filters': {'polarization': 'RR'}}

        self.assertIsInstance(self.ms.get_phase_data(filter_params), PhaseSet)
        self.casa_measurement_set.getdata.assert_called_with(['phase'])
        phase_set_init.assert_called_with(self.phase_set_data['phase'][0][0])