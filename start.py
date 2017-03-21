import os, sys
from shutil import copyfile
from sys import path
path.append("src/main/python")
from cleanup import clean
from configs import config
from main import main

dataset_path = sys.argv[1]

def output_path(dataset_path):
    dataset_name = os.path.splitext(os.path.basename(dataset_path))[0]
    config.OUTPUT_PATH = config.OUTPUT_PATH + "/" + dataset_name
    if not os.path.exists(config.OUTPUT_PATH):
        os.makedirs(config.OUTPUT_PATH)
    return config.OUTPUT_PATH

def snapshot_config():
    copyfile("conf/config.yml", config.OUTPUT_PATH+"/config.yml")

clean()
output_path(dataset_path)
snapshot_config()
main(dataset_path)
