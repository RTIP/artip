from sys import path
from pybuilder.core import use_plugin, init, task

path.append("src/main/python")
from configs import config, pipeline_config, logging_config
import start
from main import main
from profiler import Profiler
from conditional import conditional

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.distutils")
use_plugin("copy_resources")
use_plugin("python.install_dependencies")

name = "artip"
default_task = ["clean", "install_dependencies", "publish"]


@init
def set_dependencies(project):
    # Build dependencies
    project.build_depends_on('mock')
    project.build_depends_on('coloredlogs')
    project.build_depends_on('cProfile')
    project.build_depends_on('lsprofcalltree')
    project.build_depends_on('conditional')


@init
def initialize(project):
    project.get_property("copy_resources_glob").append("conf/*.yml")
    project.get_property("copy_resources_glob").append("casa_scripts/*.py")
    project.get_property("copy_resources_glob").append("build.py")
    project.install_file("conf/*.yml", "conf/*.yml")
    project.install_file("casa_scripts/*.py", "casa_scripts/*.py")
    project.install_file("build.py", 'build.py')


@init
def set_properties(project):
    project.version = "1.0"
    project.set_property("distutils_commands", ["sdist"])
    project.set_property("copy_resources_target", "$dir_dist")
    project.set_property('integrationtest_always_verbose', True)
    project.set_property("integrationtest_inherit_environment", True)
    # project.set_property('integrationtest_parallel', True)


@task
def run_integration_tests():
    start.clean()


@task
def run(project):
    pipeline_config.load("conf/pipeline_config.yml")

    with conditional(pipeline_config.PIPELINE_CONFIGS['code_profiling'], Profiler()):
        dataset_path = project.get_property("dataset")
        config_path = "conf/config.yml"
        logging_config.load()
        config.load(config_path)
        start.create_output_dir(dataset_path)
        start.snapshot_config(config_path)
        start.create_flag_file()
        main(dataset_path)
        start.clean()
