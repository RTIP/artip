from configs.config import ALL_CONFIGS, DATASET, CASAPY_CONFIG
import os
import subprocess
import time
import casac
import logging
from terminal_color import Color


class CasaRunner:
    @staticmethod
    def flagdata(reason):
        script_path = 'casa_scripts/flag.py'
        script_parameters = "{0} {1}".format(DATASET, reason)
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def apply_flux_calibration():
        script_path = 'casa_scripts/calibration.py'
        CasaRunner._run(script_path, DATASET)

    @staticmethod
    def apply_bandpass_calibration():
        script_path = 'casa_scripts/bandpass_calibration.py'
        source_config = ALL_CONFIGS['flux_calibration']
        field = source_config['field']
        refant = source_config['refant']
        minsnr = source_config['minsnr']
        spw = "{0}:{1}".format(source_config['spw'], source_config['channels_to_avg'])
        script_parameters = "{0} {1} {2} {3} {4}".format(DATASET, field, refant, minsnr, spw)

        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def apply_phase_calibration(flux_cal_field, phase_cal_field, channels_to_avg):
        logging.info(Color.HEADER + "Applying Phase Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/phase_calibration.py'
        script_parameters = "{0} {1} {2} {3}".format(DATASET, flux_cal_field, phase_cal_field, channels_to_avg)
        CasaRunner._run(script_path, script_parameters)
        logging.info(Color.HEADER + "Phase Calibration Applied..." + Color.ENDC)

    @staticmethod
    def r_flag(source):
        source_config = ALL_CONFIGS[source]
        r_flag_config = source_config['r_flag']
        script_path = 'casa_scripts/r_flag.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7}".format(r_flag_config['freqrange'], DATASET,
                                                                 source_config['field'],
                                                                 source_config['spw'],
                                                                 r_flag_config['freqdevscale'],
                                                                 r_flag_config['timedevscale'],
                                                                 r_flag_config['growfreq'],
                                                                 r_flag_config['growtime'])
        CasaRunner._run(script_path, script_parameters)

    @staticmethod
    def setjy(source_id, source_name):
        logging.info(Color.HEADER + 'Running setjy on Flux calibrator' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        freq_band = "L"
        model_path = "{0}/{1}_{2}.im".format(CASAPY_CONFIG['model_path'], source_name, freq_band)
        script_parameters = "{0} {1} {2}".format(DATASET, source_id, model_path)
        CasaRunner._run(script_path, script_parameters, CASAPY_CONFIG['path'])

    @staticmethod
    def _unlock_dataset(dataset):
        table = casac.casac.table()
        table.open(dataset)
        table.unlock()

    @staticmethod
    def _run(script, script_parameters=DATASET, casapy_path=CASAPY_CONFIG['path']):
        CasaRunner._unlock_dataset(DATASET)
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui -c {1} {2}".format(casapy_path, script_full_path, script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        while process.poll() is None:
            time.sleep(0.5)
