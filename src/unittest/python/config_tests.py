import unittest
from config import Config


class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = Config('conf/config.yml')

    def test_should_return_global_configs(self):
        expected = {'polarizations': ['RR', 'LL']}
        self.assertEqual(self.config.global_configs(), expected)

    def test_should_return_configs_for_flux_calibration(self):
        expected = {'field': 0, 'channel': 100, 'r_threshold': 0.3}
        self.assertEqual(self.config.get('flux_calibration'), expected)

    def test_should_return_error_when_invalid_config_name_is_passed(self):
        with self.assertRaises(KeyError):
            self.config.get('invalid')