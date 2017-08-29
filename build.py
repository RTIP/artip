from sys import path
from pybuilder.core import use_plugin, init, task

path.append("src/main/python")
from configs import config, pipeline_config, logging_config
import start
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
    project.build_depends_on('lsprofcalltree')
    project.build_depends_on('conditional')


@init
def initialize(project):
    project.version = "1.0.0"
    project.get_property("copy_resources_glob").append("casa_scripts/*.py")
    project.get_property("copy_resources_glob").append("build.py")
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
    config_path = project.get_property("conf") + "/"
    config.load(config_path)
    pipeline_config.load(config_path + "pipeline_config.yml")
    with conditional(pipeline_config.PIPELINE_CONFIGS['code_profiling'], Profiler()):
        dataset_path = project.get_property("dataset")
        logging_config.load()
        start.add_configs_module_in_casa()
        start.create_output_dir(dataset_path)
        start.snapshot_config(config_path)
        from main import main
        main(dataset_path)
        start.clean()
