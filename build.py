from pybuilder.core import use_plugin, init
from sys import path
path.append("src/main/python")

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")

name = "artip"
default_task = "publish"

@init
def set_properties(project):
    print("Init task")
    pass
