import unittest
from configs import config, pipeline_config, logging_config
import start
from main import main
import os
import time
import subprocess


class FlaggingTest(unittest.TestCase):
    def __init__(self, dataset_name):
        unittest.TestCase.__init__(self, methodName='test_actual_flags_should_match_expected_flags')
        pipeline_config.load("src/integrationtest/conf/pipeline_config.yml")
        logging_config.load()
        self.dataset_path = "src/integrationtest/seed_data/"
        self.dataset_name = dataset_name
        config.load(self.dataset_path + dataset_name + "/config.yml")
        start.create_output_dir("{0}/{1}/{1}.ms".format(self.dataset_path, self.dataset_name))

    def test_actual_flags_should_match_expected_flags(self):
        dataset = "{0}/{1}/{1}.ms".format(self.dataset_path, self.dataset_name)
        main(dataset)
        actual_flags = open(config.OUTPUT_PATH + '/flags.txt').read()
        expected_flags = open("{0}/{1}/expected_flags.txt".format(self.dataset_path, self.dataset_name)).read()
        self.assertEquals(actual_flags, expected_flags)


def shortDescription(self):
    return 'Testing for... ' + self.dataset_name


def get_test_data_suite():
    dataset_names = ['may14']
    return unittest.TestSuite([FlaggingTest(dataset) for dataset in dataset_names])


if __name__ == '__main__':
    testRunner = unittest.TextTestRunner()
    testRunner.run(get_test_data_suite())
