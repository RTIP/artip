import sys
from sys import path
path.append("src/main/python")

# clear/create flag record file
flag_record_file = open('casa_scripts/flags.txt','w+')
flag_record_file.close()

ms_dataset=sys.argv[1]

from configs import config
config.DATASET_PATH = ms_dataset

from main import main
from cleanup import clean
clean()
main()

