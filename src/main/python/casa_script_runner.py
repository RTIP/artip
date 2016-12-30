from configs.config import DATASET, CASAPY_CONFIG
import subprocess
import time
from datetime import datetime


class CasaScriptRunner:
    @staticmethod
    def run(script, measurement_set=DATASET, casapy_path=CASAPY_CONFIG['path']):
        command = casapy_path + ' --nologger' + ' --nogui' + ' -c ' + script + ' '
        process = subprocess.Popen(command + measurement_set, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        print "Casapy Process Started", str(datetime.now())
        print 'process Id=', process.pid
        while process.poll() is None:
            time.sleep(0.5)
        print "Casapy Process Completed", str(datetime.now())
