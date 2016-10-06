#! /bin/bash
#
# WARNING: this version of casapy is not from the CASA source tree.  It is maintained under
# https://svn.cv.nrao.edu/svn/casa/development_tools/packaging/OS-X/
#
export PYTHONIOENCODING=UTF-8
startDir=$(pwd)
OSVERS=$(uname -r | awk -F. '{print $1}')
if [ $OSVERS -lt "11" ]; then
   echo "The version of CASA you have downloaded is incompatible with your OS"
   echo "I'm expecting to run on 10.7, Lion"
   exit
fi
export LC_CTYPE=en_US.UTF-8

RUNDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

a_site="socorro"

if [[ -L "$0"  ]]; then
	real_me=$(/usr/bin/stat -f %Y "$0")
	myDir=$(dirname "$real_me")
	echo -n '==>  '
else
	myDir=$(dirname "$0")
fi

_dorsync="T"
if [ "$1" = "--norsync" ]; then
	  _dorsync="F"
fi

#prefix=$(dirname "${myDir}")
#echo "mydirprefix" $prefix
#prefix=$(cd "$( dirname "$RUNDIR" )" && pwd )
#echo "rundirprefix" $prefix
#echo "Curr dir:"$0
prefix=$(readlink $0)

#echo "readlinkprefix '$prefix'"

if [ -n "$prefix" ] ; then
    prefix=$(dirname $prefix |sed -e "s/\/MacOS//")
fi
 
#echo "readlinkprefix" $prefix

if [ -z "$prefix" ] || [ "$prefix" == "." ]; then
    prefix=$(cd "$( dirname "$RUNDIR" )" && pwd )
fi

a_root="${prefix}"
a_host=$(hostname -s)
a_arch=$(uname -p)
a_site="${a_site}-${a_arch}"
a_arch="darwin"

p_root=${prefix}/Frameworks/Python.framework/Versions/2.7
p_bind=${p_root}/MacOS
p_libd=${p_root}/lib/python2.7
p_path=${p_bind}:${p_libd}:${p_libd}/plat-mac:${p_libd}/plat-darwin:${p_bind}/lib-scriptpackages:${p_libd}/lib-tk:${p_libd}/lib-dynload:${p_libd}/site-packages:${p_libd}/site-packages/Numeric:${p_libd}/site-packages/PyObjC

export   __CASAPY_PYTHONDIR=/usr/bin/python   #${prefix}/Resources/python
p_path=${__CASAPY_PYTHONDIR}:${p_path}


export CASACORE_LDPATH=${prefix}/Plugins/casa/
#export PYTHONHOME=${p_root}
#export PYTHONPATH=${p_libd}/site-packages/readline:${p_path}
#export PYTHONEXECUTABLE=${prefix}/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
export CASAPATH="$a_root $a_arch $a_site $a_host"
export PGPLOT_DIR="${prefix}/Resources/pgplot"
export DISPLAY=${DISPLAY=:0.0}
export PATH="${prefix}/MacOS:/bin:/sbin:/usr/bin:/usr/sbin"
export LESS=${LESS="-X"}
export MPLCONFIGDIR=${HOME}/.casa
if [ ! -d "$MPLCONFIGDIR" ]; then
   mkdir -p "$MPLCONFIGDIR"
fi
if [ ! -d "$MPLCONFIGDIR" ]; then
   echo "could not create matplotlib config directory: $MPLCONFIGDIR"
   exit 1
fi
if [ -e "${HOME}/.casa/fontList.cache" -a ! -e "${MPLCONFIGDIR}/fontList.cache" ]; then
   mv "${HOME}/.casa/fontList.cache" "$MPLCONFIGDIR"
fi 

export TCL_LIBRARY="${prefix}/Resources/tcl"
export TK_LIBRARY="${prefix}/Resources/tk"

unset  LD_LIBRARY_PATH
unset  DYLD_LIBRARY_PATH
unset  DYLD_FRAMEWORK_PATH
unset  DYLD_FALLBACK_FRAMEWORK_PATH

if [ ! -z ${CASALD_LIBRARY_PATH+x} ]; then
    echo "CASALD_LIBRARY_PATH environment variable is set."
    export LD_LIBRARY_PATH=$CASALD_LIBRARY_PATH
    echo "Setting LD_LIBRARY_PATH to $LD_LIBRARY_PATH"
fi

export TERMINFO="${prefix}/Resources/terminfo"


if [ ${#PGPLOT_DIR} -gt 112 ]
then
	echo
	echo
	echo "======================================================================"
	echo
	echo "WARNING: The runtime for PGPLOT limits path lengths to 112 characters."
	echo "WARNING: The current CASA application location"
	echo "WARNING:   " ${prefix}
	echo "WARNING:     results in a path that is " ${#PGPLOT_DIR} " characters."
	echo "WARNING: You may experience problems with the CASA viewer and imager."
	echo "WARNING: Please exit CASA, then move the CASA application"
	echo "WARNING:  to /Applications and try again."
	echo
	echo "======================================================================"
	echo
	echo
fi

# Source possible local CASA initialization files.
for ci in \
	${a_root}/.casainit.sh \
	${a_root}/aips++local.sh \
	${a_root}/${a_arch}/aips++local.sh \
	${a_root}/${a_arch}/${a_site}/aips++local.sh \
	${a_root}/${a_arch}/${a_site}/${a_host}/aips++local.sh \
	${HOME}/.aips++local.sh \
	${HOME}/.casainit
do
  if  [ -r $ci ]; then
	$verbose && echo "sourcing $ci"
	. $ci
  fi
done


if [ -w ${prefix}/Library/LaunchDaemons/org.freedesktop.dbus-system.plist ]; then
    sed -i .bak -e "s,>/.*/Contents,>${prefix},g" ${prefix}/Library/LaunchDaemons/org.freedesktop.dbus-system.plist
fi
if [ -w ${prefix}/Library/LaunchAgents/org.freedesktop.dbus-session.plist ]; then
    sed -i .bak -e "s,>/.*/Contents,>${prefix},g" ${prefix}/Library/LaunchAgents/org.freedesktop.dbus-session.plist
fi
if [ -w ${prefix}/Library/LaunchDaemons/org.freedesktop.dbus-system.plist ]; then
    sed -i .bak -e "s,--config-file=.*/Contents,--config-file=${prefix},g" ${prefix}/Library/LaunchDaemons/org.freedesktop.dbus-system.plist
fi
if [ -w ${prefix}/Library/LaunchAgents/org.freedesktop.dbus-session.plist ]; then
    sed -i .bak -e "s,--config-file=.*/Contents,--config-file=${prefix},g" ${prefix}/Library/LaunchAgents/org.freedesktop.dbus-session.plist
fi
if [ -w ${prefix}/Resources/dbus-1/system.conf ]; then
    sed -i .bak -e "s,servicehelper>.*/Contents,servicehelper>${prefix},g" ${prefix}/Resources/dbus-1/system.conf
fi
if [ -w ${prefix}/Resources/dbus-1/system.conf ]; then
    sed -i .bak -e "s,pidfile>.*/Contents,pidfile>${prefix},g" ${prefix}/Resources/dbus-1/system.conf
fi
if [ -w ${prefix}/Resources/dbus-1/system.conf ]; then
    sed -i .bak -e "s,unix:path=.*/Contents,unix:path=${prefix},g" ${prefix}/Resources/dbus-1/system.conf
fi
#
# Here we check that both dbus launchctl processes are running, if not shutdown the orphan and proceed
# S Rankin - obsolete - commented out
# _checkdbus=$(launchctl list | grep freedesktop | wc -l | tr -d ' ')
# if [ "${_checkdbus}" -eq "1" ]; then
#   _dbusctl=$(launchctl list | grep freedesktop | awk '{print $3}')
#   launchctl remove ${_dbusctl}
# fi
# launchctl load ${prefix}/Library/LaunchDaemons/org.freedesktop.dbus-system.plist
# launchctl load ${prefix}/Library/LaunchAgents/org.freedesktop.dbus-session.plist

echo
echo "========================================="
echo "The start-up time of CASA may vary"
echo "depending on whether the shared libraries"
echo "are cached or not."
echo "========================================="
echo

casapy_wdir=$(defaults read edu.nrao.casa.macosx.casapy casapy.working.dir 	2>/dev/null)
if (( ${#casapy_wdir} > 0 )); then
	mkdir -p "$casapy_wdir"
	cd "$casapy_wdir" && echo "=== cd: "$(pwd)" ==="
	echo "==="
else
	cd $startDir
fi


# This bit of code, copies the old casapy.log file to one with a
# date string based on the last entry and then blows away the casapy.log
# after creating a hard link

if [[ -f casapy.log ]]; then
	ln casapy.log casapy.$(tail -n 1 casapy.log | cut -c 1-19 | tr ' ' T).log && rm casapy.log
fi



casapy_opts=$(defaults read edu.nrao.casa.macosx.casapy casapy.opts 		2>/dev/null)

export OMP_NUM_THREADS=${OMP_NUM_THREADS:="1"}

#exec -a casapy ${prefix}/MacOS/ipython -pylab
#exec  -a casapy ${prefix}/MacOS/casaCpy $casapy_opts $*
#exec -a pythonw ${prefix}/MacOS/pythonw -W ignore::DeprecationWarning ${prefix}/Resources/python/casapy.py "$@"
echo "hello"
/usr/bin/python 
#/usr/bin/python /Users/dollyg/Projects/IUCAA/artip/src/main/python/start.py
#/usr/local/bin/pyb run

#
# O_o
