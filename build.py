import sys
import os

sys.path.insert(0, 'src/main/python')
from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")
use_plugin("copy_resources")

name = "artip"
summary = "Automated Radio Telescope Imaging Pipeline"
description = """Automated Radio Telescope Image Processing Pipeline (ARTIP) is an end to end pipeline
automating the entire process of flagging, calibration and imaging for radio-interferometric data.

ARTIP starts with raw data i.e. a Measurement Set and goes through multiple stages like
Flux Calibration, Bandpass Calibration, Phase Calibration and Imaging to generate continuum and spectral line images.
"""

authors = [Author("ARTIP Team", "artip@googlegroups.com")]
url = "https://github.com/RTIP/artip"
license = "GPL License"
default_task = ["clean", "install_dependencies", "publish"]
pipeline_conf_install_path = os.getenv("HOME") + "/" + "conf"


@init
def initialize(project):
    project.version = "1.0.0"
    project.set_property("pdoc_module_name", "artip")
    project.set_property('include_package_data', True)
    project.get_property("copy_resources_glob").append("environment.yml")
    project.get_property("copy_resources_glob").append("casa_dependencies.txt")
    project.get_property("copy_resources_glob").append("setup_casapy_pip.py")
    project.get_property("copy_resources_glob").append("casa_scripts/*.py")
    project.get_property("copy_resources_glob").append("conf/*")
    project.set_property("copy_resources_target", "$dir_dist/artip")
    project.package_data.update({'artip': ["casa_dependencies.txt", "environment.yml", "conf/*", "casa_scripts/*"]})


@init(description="Copy dependencies file to .artip directory in users home")
def initialize2(project):
    source_directory = "build/lib/artip"
    destination = "etc/.dependencies"
    project.files_to_install.append((destination, ["{0}/environment.yml".format(source_directory),
                                                   "{0}/casa_dependencies.txt".format(source_directory),
                                                   "{0}/setup_casapy_pip.py".format(source_directory)]))


@init(description="Copying all pipeline configs to user home directory")
def initialize3(project):
    source_directory = 'build/lib/artip/conf'
    destination = "etc/configs"
    project.files_to_install.append((destination, ["{0}/auto_flagging_config.yml".format(source_directory),
                                                   "{0}/calibration.yml".format(source_directory),
                                                   "{0}/casa.yml".format(source_directory),
                                                   "{0}/imaging.yml".format(source_directory),
                                                   "{0}/pipeline.yml".format(source_directory),
                                                   "{0}/target_source.yml".format(source_directory),
                                                   "{0}/user_defined_flags.txt".format(source_directory)]))
