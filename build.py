from sys import path
from pybuilder.core import use_plugin, init, task
from packager import Packager

path.append("src/main/python")
from configs import config, logging_config
import start
from profiler import Profiler
from conditional import conditional

use_plugin("python.core")
use_plugin("python.distutils")

name = "artip"
default_task = ["clean"]


@init
def initialize(project):
    project.version = "1.0"


@task
def package(project):
    filename = 'target/artip_{0}.zip'.format(project.version)
    root_directory = '.'
    packager = Packager(filename, root_directory)
    packager.package()


@task
def run(project):
    config_path = project.get_property("conf") + "/"
    config.load(config_path)
    with conditional(config.PIPELINE_CONFIGS['code_profiling'], Profiler()):
        dataset_path = project.get_property("dataset")
        logging_config.load()
        start.add_configs_module_in_casa()
        start.create_output_dir(dataset_path)
        start.snapshot_config(config_path)
        from main import main
        main(dataset_path)
        start.clean()
