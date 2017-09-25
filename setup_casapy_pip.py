from __future__ import print_function

import os
import errno
import stat
import tempfile
import subprocess
import platform
import ssl

from distutils.spawn import find_executable
from hashlib import md5
from urllib import urlopen

USER_DIR = os.path.join(os.path.expanduser('~'), '.casa')
BIN_DIR = os.path.join(os.path.expanduser('~'), '.casa', 'bin')
USER_SITE = os.path.join(os.path.expanduser('~'), '.casa', 'lib', 'python{pv}', 'site-packages')

PIP_URL = "https://pypi.python.org/packages/11/b6/abcb525026a4be042b486df43905d6893fb04f05aac21c32c638e939e447/pip-9.0.1.tar.gz"
PIP_MD5 = "35f01da33009719497f01a4ba69d63c9"

SETUPTOOLS_URL = "https://pypi.python.org/packages/a9/23/720c7558ba6ad3e0f5ad01e0d6ea2288b486da32f053c73e259f7c392042/setuptools-36.0.1.zip"
SETUPTOOLS_MD5 = "430eb106788183eefe9f444a300007f0"


def mkdir_p(path):
    # Create a directory using mkdir -p
    # Solution provided on StackOverflow
    try:
        os.makedirs(path)
    except OSError as exc:
        if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
            raise


def make_executable(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


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


def get_python_version_mac():
    casapy_path = get_casapy_path()
    parent = os.path.dirname(casapy_path)
    python = os.path.join(parent, 'python')
    p = subprocess.Popen([python, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    version = p.stderr.read().split()[1][:3]
    print("Determined Python version in CASA... {0}".format(version))
    return version


def get_python_path_linux():
    """ get the version and the appropriate parent directory path """
    casapy_path = get_casapy_path()
    parent = os.path.dirname(casapy_path)
    grandparent = os.path.dirname(parent)
    version = None
    for lib in ('lib64', 'lib'):
        if os.path.exists(os.path.join(grandparent, lib, 'python2.7')):
            version = "2.7"
            path = grandparent
        elif os.path.exists(os.path.join(grandparent, lib, 'python2.6')):
            version = "2.6"
            path = grandparent
        elif os.path.exists(os.path.join(parent, lib, 'python2.7')):
            version = "2.7"
            path = parent
        elif os.path.exists(os.path.join(parent, lib, 'python2.6')):
            version = "2.6"
            path = parent
        if version is not None:
            break
    if version is None:
        raise ValueError("Could not determine Python version")
    return version, path, lib


def get_python_version_linux():
    version, casapy_parent_path, lib = get_python_path_linux()
    print("Determined Python version in CASA... {0}".format(version))
    return version


def install_package(pv="2.7", packagename='pip', url=PIP_URL, md5_checksum=PIP_MD5):
    print("Downloading {0}...".format(packagename))

    # Create temporary directory

    tmpdir = tempfile.mkdtemp(dir='/tmp')
    os.chdir(tmpdir)

    # Download module and expand
    context = ssl._create_unverified_context()
    content = urlopen(url, context=context).read()

    if md5(content).hexdigest() != md5_checksum:
        raise ValueError("checksum does not match")

    with open(os.path.basename(url), 'wb') as f:
        f.write(content)

    # Prepare installation script

    print("Installing {0}...".format(packagename))

    site_packages = os.path.expanduser('~/.casa/lib/python{pv}/site-packages'.format(pv=pv))
    mkdir_p(site_packages)

    PKG_INSTALL = """
#!/bin/bash
export PYTHONUSERBASE=$HOME/.casa
export PATH=$HOME/.casa/bin:$PATH
{extraction_command} {pkg_filename}
cd {pkg_name}
casa-python setup.py install --prefix=$HOME/.casa
    """

    pkg_filename = os.path.basename(url)
    extraction_command = None

    if packagename == 'pip':
        pkg_name = pkg_filename.rsplit('.', 2)[0]
        extraction_command = 'tar xvzf'
    if packagename == 'setuptools':
        pkg_name = pkg_filename.rsplit('.', 1)[0]
        extraction_command = 'unzip'
    with open('install_pkg.sh', 'w') as f:
        f.write(PKG_INSTALL.format(pkg_filename=pkg_filename, pkg_name=pkg_name, extraction_command=extraction_command))

    make_executable('install_pkg.sh')

    # Need to use subprocess instead
    retcode = os.system('./install_pkg.sh')
    os.system("rm -r {0}".format(tmpdir))
    if retcode != 0:
        raise SystemError("{0} installation failed!".format(packagename))


def write_casa_python_mac(pv="2.7"):
    print("Creating casa-python script...")

    TEMPLATE_PYTHON = """
#!/bin/sh

INSTALLPATH={casapy_path}

PROOT=$INSTALLPATH/Frameworks/Python.framework/Versions/{pv}
PBIND=$PROOT/MacOS
PLIBD=$PROOT/lib/python{pv}
PPATH=$PBIND:$PLIBD:$PLIBD/plat-mac:$PLIBD/plat-darwin
PPATH=$PPATH:$PBIND/lib-scriptpackages:$PLIBD/lib-tk
PPATH=$PPATH:$PLIBD/lib-dynload:$PLIBD/site-packages
PPATH=$PPATH:$PLIBD/site-packages/Numeric:$PLIBD/site-packages/PyObjC
PPATH=$INSTALLPATH/Resources/python:$PPATH

export PYTHONUSERBASE=$HOME/.casa

export PYTHONHOME=$PROOT
export PYTHONPATH={user_site2}:$PPATH
export PYTHONPATH={user_site}:$PPATH
export PYTHONEXECUTABLE=$PROOT/Resources/Python.app/Contents/MacOS/Python

export DYLD_FRAMEWORK_PATH="$INSTALLPATH/Frameworks"

exec -a pythonw $INSTALLPATH/MacOS/pythonw -W ignore::DeprecationWarning "$@"
    """

    mkdir_p(BIN_DIR)

    casapy_path = os.path.dirname(os.path.dirname(get_casapy_path()))

    # On some installs of CASA, the user-site uses a python-version-independent
    # site-packages directory, which has something to do with the way USER_SITE
    # is set for OSX Frameworks.  We therefore add a second directory to the
    # path BEHIND the "correct" python version path.

    with open(os.path.join(BIN_DIR, 'casa-python'), 'w') as f:
        f.write(TEMPLATE_PYTHON.format(casapy_path=casapy_path, pv=pv,
                                       user_site2=USER_SITE.format(pv=''),
                                       user_site=USER_SITE.format(pv=pv)))

    make_executable(os.path.join(BIN_DIR, 'casa-python'))


def write_casa_python_linux(pv="2.7"):
    print("Creating casa-python script...")

    TEMPLATE_PYTHON = """
#!/bin/sh

INSTALLPATH={casapy_path}

export LD_LIBRARY_PATH=$INSTALLPATH/{lib}:/{lib}:/usr/{lib}:$LD_LIBRARY_PATH
export LDFLAGS="-L$INSTALLPATH/{lib}/"

export PYTHONHOME=$INSTALLPATH

export PYTHONUSERBASE=$HOME/.casa

export PYTHONPATH=$INSTALLPATH/{lib}/python{pv}/site-packages:$PYTHONPATH
export PYTHONPATH=$INSTALLPATH/{lib}/python{pv}/heuristics:$PYTHONPATH
export PYTHONPATH=$INSTALLPATH/{lib}/python{pv}:$PYTHONPATH

exec $INSTALLPATH/{lib}/{lib_casapy}/bin/python $*
    """

    mkdir_p(BIN_DIR)

    # vers is throwaway here
    vers, casapy_path, lib = get_python_path_linux()
    # parent directory of 'bin' changed from casapy -> casa from 4.2 to 4.3?
    lib_casapy = {'lib64': 'casapy',
                  'lib': 'casa'}

    with open(os.path.join(BIN_DIR, 'casa-python'), 'w') as f:
        f.write(TEMPLATE_PYTHON.format(casapy_path=casapy_path, pv=pv,
                                       lib=lib, lib_casapy=lib_casapy[lib]))

    make_executable(os.path.join(BIN_DIR, 'casa-python'))


def write_casa_pip():
    print("Creating casa-pip script...")

    TEMPLATE_PIP = """
$HOME/.casa/bin/casa-python $HOME/.casa/bin/pip $* --user
    """

    with open(os.path.join(BIN_DIR, 'casa-pip'), 'w') as f:
        f.write(TEMPLATE_PIP)

    make_executable(os.path.join(BIN_DIR, 'casa-pip'))


def write_init(pv="2.7"):
    print("Creating init.py script...")

    TEMPLATE_INIT = """
import site
site.addsitedir("{site_packages}")
site.addsitedir("{site_packages_noversion}")
    """

    with open(os.path.join(USER_DIR, 'init.py'), 'a') as f:
        f.write(TEMPLATE_INIT.format(site_packages=USER_SITE.format(pv=pv),
                                     site_packages_noversion=USER_SITE.format(pv='')))


def add_bin_to_path():
    if BIN_DIR not in os.environ["PATH"]:
        os.environ["PATH"] += BIN_DIR + os.pathsep
        print("{0} added to your PATH please run 'source <rc file>'".format(BIN_DIR))


if __name__ == "__main__":

    if platform.system() == 'Darwin':

        python_version = get_python_version_mac()
        write_casa_python_mac(pv=python_version)

    else:

        python_version = get_python_version_linux()
        write_casa_python_linux(pv=python_version)

    install_package(pv=python_version, packagename='setuptools',
                    url=SETUPTOOLS_URL, md5_checksum=SETUPTOOLS_MD5)
    install_package(pv=python_version, packagename='pip', url=PIP_URL,
                    md5_checksum=PIP_MD5)
    write_casa_pip()
    write_init(pv=python_version)

    add_bin_to_path()
