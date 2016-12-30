from configs.config import DATASET, CASAPY_CONFIG
import os
import subprocess
import time
from datetime import datetime


class CasaScriptRunner:
    @staticmethod
    def _run(script, script_parameters=DATASET, casapy_path=CASAPY_CONFIG['path']):
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui -c {1} {2}".format(casapy_path, script_full_path, script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        print "Casapy Process Started", str(datetime.now())
        print 'process Id=', process.pid
        while process.poll() is None:
            time.sleep(0.5)
        print "Casapy Process Completed", str(datetime.now())

    @staticmethod
    def flagdata(reason):
        script_path = 'casa_scripts/flag.py'
        script_parameters = "{0} {1}".format(DATASET, reason)
        CasaScriptRunner._run(script_path, script_parameters, CASAPY_CONFIG['path'])
