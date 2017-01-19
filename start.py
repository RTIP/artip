import sys
import os
from sys import path

path.append("src/main/python")

ms_dataset = sys.argv[1]

from configs import config

config.DATASET_PATH = ms_dataset

# clear/create flag record file
flag_file_name = "{0}_flags.txt".format(os.path.splitext(os.path.basename(ms_dataset))[0])
config.FLAG_FILE = "{0}/{1}".format(config.GLOBAL_CONFIG['flag_file_directory'], flag_file_name)

flag_record_file = open(config.FLAG_FILE, 'w+')
flag_record_file.close()

from main import main
from cleanup import clean

clean()
main()
