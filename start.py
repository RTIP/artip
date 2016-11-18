import sys
from sys import path
path.append("src/main/python")

ms_dataset=sys.argv[1]

from main import main
main(ms_dataset)

