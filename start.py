import os, sys
from sys import path
path.append("src/main/python")
from cleanup import clean
from configs import config
config.DATASET_PATH = sys.argv[1]

def setup():
    dataset_name = os.path.splitext(os.path.basename(config.DATASET_PATH))[0]
    config.OUTPUT_PATH = config.GLOBAL_CONFIG['output_path'] + "/" + dataset_name
    if not os.path.exists(config.OUTPUT_PATH):
        os.makedirs(config.OUTPUT_PATH)
    config.FLAG_FILE = "{0}/flags.txt".format(config.OUTPUT_PATH)

    flag_record_file = open(config.FLAG_FILE, 'w+')
    flag_record_file.close()

setup()

from main import main
clean()
main()
