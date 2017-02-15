import os, sys
from sys import path
path.append("src/main/python")
from cleanup import clean
from main import main


clean()
dataset_path = sys.argv[1]
main(dataset_path)
