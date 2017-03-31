import unittest
from configs import config, pipeline_config, logging_config
import start
from main import main
from os import listdir
from shutil import rmtree
from test_helper import fits_to_ms


class FlaggingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pipeline_config.load("src/integrationtest/conf/pipeline_config.yml")
        logging_config.load()

    def __init__(self, dataset_name):
        unittest.TestCase.__init__(self, methodName='test_actual_flags_should_match_expected_flags')
        self.seed_data_path = "src/integrationtest/seed_data/"
        self.dataset_name = dataset_name

    def setUp(self):
        config.load(self.seed_data_path + self.dataset_name + "/config.yml")
        self.ms_file = "{0}/{1}/{1}.ms".format(config.OUTPUT_PATH, self.dataset_name)
        fits_file = "{0}/{1}/{1}.fits".format(self.seed_data_path, self.dataset_name)
        start.create_output_dir(fits_file)
        fits_to_ms(fits_file, self.ms_file)

    def test_actual_flags_should_match_expected_flags(self):
        self.assert_flagging()

    def assert_flagging(self):
        main(self.ms_file)
        actual_flags = open(config.OUTPUT_PATH + '/flags.txt').read()
        expected_flags = open("{0}/{1}/expected_flags.txt".format(self.seed_data_path, self.dataset_name)).read()
        self.assertEquals(actual_flags, expected_flags, msg="Dataset= " + self.ms_file)


def get_test_data_suite():
    dataset_names = filter(lambda file_name: not file_name.startswith('.'), listdir('src/integrationtest/seed_data/'))
    return unittest.TestSuite([FlaggingTest(dataset) for dataset in dataset_names])


if __name__ == '__main__':
    testRunner = unittest.TextTestRunner()
    testRunner.run(get_test_data_suite())
