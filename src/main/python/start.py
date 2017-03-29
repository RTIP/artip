from os import path,listdir,makedirs, remove
from re import search
from shutil import copyfile, rmtree
from configs import config

def create_output_dir(dataset_path):
    dataset_name = path.splitext(path.basename(dataset_path))[0]
    config.OUTPUT_PATH = config.OUTPUT_PATH + "/" + dataset_name
    if not path.exists(config.OUTPUT_PATH):
        makedirs(config.OUTPUT_PATH)
    return config.OUTPUT_PATH

def clean():
    dir = "."
    patterns = [".log", ".last"]
    for f in listdir(dir):
        for pattern in patterns:
            if search(pattern, f):
                f = path.join(dir, f)
                if path.isdir(f):
                    rmtree(f)
                else:
                    remove(f)



def snapshot_config(config_path):
    copyfile(config_path, config.OUTPUT_PATH+"/config.yml")

