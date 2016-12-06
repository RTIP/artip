import unittest
from unittest import TestCase
from measurement_set import MeasurementSet
from models.phase_set import PhaseSet
from models.antenna import Antenna
import mock
from mock import Mock


class TestMeasurementSet(TestCase):
    @mock.patch('casac.casac')
    def setUp(self, mock_casac):
        self.casa_measurement_set = Mock(name='casa_ms')
        self.mocked_meta_data = Mock(name='metadata')
        self.casa_measurement_set.metadata.return_value = self.mocked_meta_data
        self.mocked_meta_data.scannumbers.return_value = range(1, 7, 1)
        self.phase_set_data = {'phase': [[[-2.85, -1.2, 2.1, -2.3, -2.8]]]}
        mock_casac.ms.return_value = self.casa_measurement_set
        self.ms = MeasurementSet('ms_file_path')
        self.casa_measurement_set.open.assert_called_with("ms_file_path")
        self.casa_measurement_set.getdata.return_value = self.phase_set_data

    def test_get_phase_data_should_select_channel_and_polarisation(self):
        channel = {'start': 100}
        self.ms.get_phase_data(channel, 'RR')

        self.casa_measurement_set.selectinit.assert_called_with(reset=True)
        self.casa_measurement_set.selectpolarization.assert_called_with('RR')
        self.casa_measurement_set.selectchannel.assert_called_with(**channel)
        self.casa_measurement_set.select.assert_not_called()

    def test_get_phase_data_should_select_filters(self):
        filters = {'antenna1': 0, 'antenna2': 1}

        channel = {'start': 100}
        self.ms.get_phase_data(channel, 'RR', filters)

        self.casa_measurement_set.selectinit.assert_called_with(reset=True)
        self.casa_measurement_set.selectpolarization.assert_called_with('RR')
        self.casa_measurement_set.selectchannel.assert_called_with(**channel)
        self.casa_measurement_set.select.assert_called_with(filters)

    @mock.patch("models.phase_set.PhaseSet.__init__")
    def test_get_phase_data_should_return_PhaseSet_instance(self, phase_set_init):
        phase_set_init.return_value = None

        self.assertIsInstance(self.ms.get_phase_data({'start': 100}, 'RR'), PhaseSet)
        self.casa_measurement_set.getdata.assert_called_with(['phase'], ifraxis=False)
        phase_set_init.assert_called_with(self.phase_set_data['phase'][0][0])

    def test_should_return_scan_ids_for_given_source(self):
        self.mocked_meta_data.scansforfield.return_value = ['1', '2']
        self.ms.scan_ids_for(0)
        self.mocked_meta_data.scansforfield.assert_called_with(0)
        self.assertEqual(self.ms.scan_ids_for(0), [1, 2])

    def test_should_return_empty_scan_ids_for_invalid_source(self):
        invalid_source = 100
        self.mocked_meta_data.scansforfield.side_effect = RuntimeError()
        self.ms.scan_ids_for(invalid_source)
        self.mocked_meta_data.scansforfield.assert_called_with(invalid_source)
        self.assertEqual(self.ms.scan_ids_for(invalid_source), [])

    @unittest.skip("Disabled because of antennaids count mismatch between ms file summary and antennaids() method")
    def test_should_return_baselines(self):
        self.mocked_meta_data.antennaids.return_value = [1, 2, 3]
        self.assertEqual(self.ms.baselines(), [(1, 2), (1, 3), (2, 3)])

    @unittest.skip("Disabled because of antennaids count mismatch between ms file summary and antennaids() method")
    def test_should_return_baselines_with_specified_antenna(self):
        antenna2 = Antenna(2)
        antenna1 = Antenna(1)
        antenna0 = Antenna(0)
        self.mocked_meta_data.antennaids.return_value = [0, 1, 2]
        self.assertItemsEqual(self.ms.baselines_for(self.ms.antennas[0]), [(antenna1, antenna2), (antenna0, antenna2)])
