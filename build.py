from sys import path
from pybuilder.core import use_plugin, init, task
path.append("src/main/python")
from configs import config, pipeline_config, logging_config
import start
from main import main

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")

name = "artip"
default_task = ["clean", "install_dependencies", "publish"]


@init
def set_dependencies(project):
    # Build dependencies
    project.build_depends_on('mock')
    project.build_depends_on('coloredlogs')


@init
def set_properties(project):
    project.set_property('integrationtest_always_verbose', True)
    project.set_property("integrationtest_inherit_environment", True)
    # project.set_property('integrationtest_parallel', True)

@task
def run_integration_tests():
    start.clean()

@task
def run(project):
    dataset_path = project.get_property("dataset")
    config_path = "conf/config.yml"

    pipeline_config.load("conf/pipeline_config.yml")
    logging_config.load()
    config.load(config_path)
    start.snapshot_config(config_path)
    start.create_output_dir(dataset_path)
    main(dataset_path)
    start.clean()
