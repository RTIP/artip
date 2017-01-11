from configs.config import DATASET, CASAPY_CONFIG, FLUX_CAL_CONFIG
import os
import subprocess
import time
import casac
import logging
from terminal_color import Color


class CasaRunner:
    @staticmethod
    def _run(script, script_parameters=DATASET, casapy_path=CASAPY_CONFIG['path']):
        CasaRunner._unlock_dataset(DATASET)
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui -c {1} {2}".format(casapy_path, script_full_path, script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        while process.poll() is None:
            time.sleep(0.5)

    @staticmethod
    def flagdata(reason):
        script_path = 'casa_scripts/flag.py'
        script_parameters = "{0} {1}".format(DATASET, reason)
        CasaRunner._run(script_path, script_parameters, CASAPY_CONFIG['path'])

    @staticmethod
    def apply_flux_calibration():
        script_path = 'casa_scripts/calibration.py'
        CasaRunner._run(script_path, DATASET, CASAPY_CONFIG['path'])

    @staticmethod
    def _unlock_dataset(dataset):
        table = casac.casac.table()
        table.open(dataset)
        table.unlock()

    @staticmethod
    def setjy(field_name):
        logging.info(Color.HEADER + 'Running setjy on Flux calibrator' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        field = FLUX_CAL_CONFIG['field']
        freq_band = "L"
        model_path =   "{0}/{1}_{2}.im".format(CASAPY_CONFIG['model_path'], field_name, freq_band)
        script_parameters = "{0} {1} {2}".format(DATASET, field, model_path)
        CasaRunner._run(script_path, script_parameters, CASAPY_CONFIG['path'])

