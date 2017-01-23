from configs.config import ALL_CONFIGS, DATASET_PATH, CASAPY_CONFIG, FLAG_FILE
import os
import subprocess
import time
import casac
import logging
from terminal_color import Color


class CasaRunner:
    @staticmethod
    def flagdata(reason):
        logging.info(Color.HEADER + "Flagging " + reason + Color.ENDC)
        script_path = 'casa_scripts/flag.py'
        script_parameters = "{0} {1} {2}".format(DATASET_PATH, FLAG_FILE, reason)
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def apply_flux_calibration():
        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/flux_calibration.py'
        CasaRunner._run(script_path, DATASET_PATH)

    @staticmethod
    def apply_bandpass_calibration():
        logging.info(Color.HEADER + "Running Bandpass Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/bandpass_calibration.py'
        source_config = ALL_CONFIGS['flux_calibration']
        field = source_config['field']
        refant = source_config['refant']
        minsnr = source_config['minsnr']
        spw = "{0}:{1}".format(source_config['spw'], source_config['channels_to_avg'])
        script_parameters = "{0} {1} {2} {3} {4}".format(DATASET_PATH, field, refant, minsnr, spw)

        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def apply_phase_calibration(flux_cal_field, phase_cal_field, channels_to_avg):
        logging.info(Color.HEADER + "Applying Phase Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/phase_calibration.py'
        script_parameters = "{0} {1} {2} {3}".format(DATASET_PATH, flux_cal_field, phase_cal_field, channels_to_avg)
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def apply_target_source_calibration(field):
        logging.info(Color.HEADER + "Applying Calibration to Target Source..." + Color.ENDC)
        script_path = 'casa_scripts/target_source_calibration.py'
        script_parameters = "{0} {1}".format(DATASET_PATH, field)
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def r_flag(source):
        source_config = ALL_CONFIGS[source]
        r_flag_config = source_config['r_flag']
        script_path = 'casa_scripts/r_flag.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7}".format(r_flag_config['freqrange'], DATASET_PATH,
                                                                     source_config['field'],
                                                                     source_config['spw'],
                                                                     r_flag_config['freqdevscale'],
                                                                     r_flag_config['timedevscale'],
                                                                     r_flag_config['growfreq'],
                                                                     r_flag_config['growtime'])
        logging.info(Color.HEADER + "Running Rflag for flagging in frequency..." + Color.ENDC)
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def setjy(source_id, source_name):
        logging.info(Color.HEADER + 'Running setjy' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        freq_band = "L"
        model_path = "{0}/{1}_{2}.im".format(CASAPY_CONFIG['model_path'], source_name, freq_band)
        script_parameters = "{0} {1} {2}".format(DATASET_PATH, source_id, model_path)
        CasaRunner._run(script_path, script_parameters, CASAPY_CONFIG['path'])

    @staticmethod
    def _unlock_dataset():
        table = casac.casac.table()
        table.open(DATASET_PATH)
        table.unlock()

    @staticmethod
    def _run(script, script_parameters=DATASET_PATH, casapy_path=CASAPY_CONFIG['path']):
        CasaRunner._unlock_dataset()
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui -c {1} {2}".format(casapy_path, script_full_path, script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        while process.poll() is None:
            time.sleep(1)
