import unittest
from configs.config_loader import ConfigLoader


class ConfigTest(unittest.TestCase):
    def test_should_load_the_given_config_file(self):
        config = ConfigLoader().load('conf/config.yml')
        actual_properties = config.keys()
        expected_properties = ['global', 'flux_calibrator', 'casapy']
        self.assertItemsEqual(expected_properties, actual_properties)
