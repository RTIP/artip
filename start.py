import sys
from sys import path
path.append("src/main/python")

ms_dataset=sys.argv[1]

from configs import config
config.DATASET = ms_dataset

from main import main
main()

