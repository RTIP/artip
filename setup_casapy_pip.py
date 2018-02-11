import platform
import os
from distutils.spawn import find_executable
import tempfile
import stat
import subprocess


def find_osx_executable(fpath='/Applications/CASA.app/Contents/MacOS/casapy'):
    if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
        return fpath


def get_casapy_path():
    casapy_path = find_executable('casa') or find_osx_executable()
    if casapy_path is None:
        raise SystemError("Could not locate casapy command")
    casapy_path = os.path.realpath(casapy_path)
    if not os.path.exists(casapy_path):
        raise SystemError("The casapy command does not point to a valid CASA installation")
    return casapy_path


def get_python_path_mac():
    casapy_path = get_casapy_path()
    parent = os.path.dirname(casapy_path)
    python = os.path.join(parent, 'python')
    return python


def get_python_path_linux():
    """ get the version and the appropriate parent directory path """
    casapy_path = get_casapy_path()
    parent = os.path.dirname(casapy_path)
    grandparent = os.path.dirname(parent)
    version = None
    for lib in ('lib64', 'lib'):
        if os.path.exists(os.path.join(grandparent, lib, 'python2.7')):
            python = grandparent
        elif os.path.exists(os.path.join(grandparent, lib, 'python2.6')):
            python = grandparent
        elif os.path.exists(os.path.join(parent, lib, 'python2.7')):
            python = parent
        elif os.path.exists(os.path.join(parent, lib, 'python2.6')):
            python = parent
        if version is not None:
            break
    if version is None:
        raise ValueError("Could not determine Python version")
    return python


def make_executable(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


if __name__ == "__main__":
    if platform.system() == 'Darwin':
        python_path = get_python_path_mac()
    else:
        python_path = get_python_path_linux()

    tmpdir = tempfile.mkdtemp(dir='/tmp')

    PIP_SETUP = """
    #!/bin/bash
    wget https://bootstrap.pypa.io/get-pip.py -P {tmpdir}
    export PYTHONUSERBASE=$HOME/.casa
    {python_path} {tmpdir}/get-pip.py --user
        """
    with open('{0}/pip_setup.sh'.format(tmpdir), 'w') as f:
        f.write(PIP_SETUP.format(python_path=python_path, tmpdir=tmpdir))

    make_executable('{0}/pip_setup.sh'.format(tmpdir))
    retcode = os.system('{0}/pip_setup.sh'.format(tmpdir))
    if retcode != 0:
        raise SystemError("pip setup failed!")

    site_packages_location = subprocess.check_output([python_path, "-m", "site", "--user-site"]).rstrip()

    casa_init_file = "{0}/.casa/init.py".format(os.environ['HOME'])
    try:
        if site_packages_location not in open(casa_init_file).read():
            with open(casa_init_file, "a") as myfile:
                myfile.write("import sys;\nsys.path.append('{0}')".format(site_packages_location))
    except IOError:
        with open(casa_init_file, 'w') as f:
            f.write("import sys;\nsys.path.append('{0}')".format(site_packages_location))

    os.system("rm -r {0}".format(tmpdir))
