import unittest
from configs.config_loader import ConfigLoader


class ConfigTest(unittest.TestCase):
    def test_should_load_the_given_config_file(self):
        config = ConfigLoader().load('conf/calibration.yml')
        actual_properties = config.keys()
        expected_properties = ['flux_calibration', 'bandpass_calibration',
                               'phase_calibration']
        self.assertItemsEqual(expected_properties, actual_properties)
