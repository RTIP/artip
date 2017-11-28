from os import path, listdir, makedirs, remove
from re import search
from distutils.dir_util import copy_tree
from shutil import rmtree
from configs import config
from os.path import expanduser


def create_output_dir(dataset_path, output_path):
    dataset_name = path.splitext(path.basename(dataset_path))[0]
    config.OUTPUT_PATH = output_path + "/" + dataset_name
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
    copy_tree(config_path, config.OUTPUT_PATH+"/conf/")
