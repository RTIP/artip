from configs.config import DATASET, CASAPY_CONFIG
import os
import subprocess
import time
from datetime import datetime


class CasaScriptRunner:
    @staticmethod
    def run(script, measurement_set=DATASET, casapy_path=CASAPY_CONFIG['path']):
        script_full_path = os.path.realpath(script)
        command = casapy_path + ' --nologger' + ' --nogui' + ' -c ' + script_full_path + ' '

        process = subprocess.Popen(command + measurement_set, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        print "Casapy Process Started", str(datetime.now())
        print 'process Id=', process.pid
        while process.poll() is None:
            time.sleep(0.5)
        print "Casapy Process Completed", str(datetime.now())
