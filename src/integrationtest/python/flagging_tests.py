import unittest
from configs import config, pipeline_config, logging_config
from configs.config_loader import ConfigLoader
import start
from main import main
from os import listdir
from test_helper import *


class FlaggingTest(unittest.TestCase):
    def __init__(self, dataset_name):
        unittest.TestCase.__init__(self, methodName='test_actual_flags_should_match_expected_flags')
        self.seed_data_path = "src/integrationtest/seed_data/"
        self.dataset_name = dataset_name

    def setUp(self):
        pipeline_config.load("src/integrationtest/conf/pipeline_config.yml")
        logging_config.load()

        config.load(self.seed_data_path + self.dataset_name + "/config.yml")
        self.ms_file = "{0}/{1}/{1}.ms".format(config.OUTPUT_PATH, self.dataset_name)
        fits_file = "{0}/{1}/{1}.fits".format(self.seed_data_path, self.dataset_name)
        start.create_output_dir(fits_file)
        fits_to_ms(fits_file, self.ms_file)

    def test_actual_flags_should_match_expected_flags(self):
        self.assert_flagging()
        self.assert_calibration()

    def assert_flagging(self):
        pipeline_config.STAGES_CONFIG.update({'flux_calibration': True, 'bandpass_calibration': True,
                                              'phase_calibration': True})
        main(self.ms_file)

        actual_flags = open(config.OUTPUT_PATH + '/flags.txt').read()
        expected_flags = open("{0}/{1}/expected_flags.txt".format(self.seed_data_path, self.dataset_name)).read()

        self.assertEquals(actual_flags, expected_flags, msg="Dataset= " + self.ms_file)


    def assert_calibration(self):
        actual_stats = get_stats(self.ms_file, config.GLOBAL_CONFIG['flux_cal_fields'])
        expected_stats_path = "{0}/{1}/expected_stats.yml".format(self.seed_data_path, self.dataset_name)
        expected_stats = ConfigLoader().load(expected_stats_path)['calibration']

        self.assertTrue(is_subset(actual_stats, expected_stats),
                        msg="Dataset={0}, actual={1}, expected={2}".format(self.ms_file, actual_stats, expected_stats))

def get_test_data_suite():
    dataset_names = filter(lambda file_name: not file_name.startswith('.'), listdir('src/integrationtest/seed_data/'))
    return unittest.TestSuite([FlaggingTest(dataset) for dataset in dataset_names])


if __name__ == '__main__':
    testRunner = unittest.TextTestRunner()
    testRunner.run(get_test_data_suite())
