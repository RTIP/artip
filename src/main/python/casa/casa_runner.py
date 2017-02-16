from configs.config import ALL_CONFIGS, CASAPY_CONFIG
import os
import subprocess
import time
import casac
import logging
from terminal_color import Color


class CasaRunner:
    def __init__(self, dataset_path, output_path):
        self._output_path = output_path
        self._dataset_path = dataset_path

    def flagdata(self, reason):
        logging.info(Color.HEADER + "Flagging " + reason + Color.ENDC)
        script_path = 'casa_scripts/flag.py'
        flag_file = self._output_path + "/flags.txt"
        script_parameters = "{0} {1} {2}".format(self._dataset_path, flag_file, reason)
        self._run(script_path, script_parameters)

    def quack(self):
        logging.info(Color.HEADER + "Running quack..." + Color.ENDC)
        script_path = 'casa_scripts/quack.py'
        self._run(script_path)

    def apply_flux_calibration(self, source_config):
        logging.info(Color.HEADER + "Applying Flux Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/flux_calibration.py'
        field = source_config['field']
        refant = source_config['casa_scripts']['refant']
        minsnr = source_config['casa_scripts']['minsnr']
        spw = "{0}:{1}".format(source_config['spw'], source_config['channel'])
        script_parameters = "{0} {1} {2} {3} {4} {5}".format(self._dataset_path, self._output_path,
                                                             field, refant, spw, minsnr)
        self._run(script_path, script_parameters)

    def apply_bandpass_calibration(self, source_config):
        logging.info(Color.HEADER + "Running Bandpass Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/bandpass_calibration.py'
        field = source_config['field']
        refant = source_config['refant']
        minsnr = source_config['minsnr']
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, self._output_path, field, refant, minsnr)

        self._run(script_path, script_parameters)

    def apply_phase_calibration(self, flux_cal_field, source_config):
        logging.info(Color.HEADER + "Applying Phase Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/phase_calibration.py'
        phase_cal_field = source_config['field']
        refant = source_config['casa_scripts']['refant']
        minsnr = source_config['casa_scripts']['minsnr']
        spw = "{0}:{1}".format(source_config['spw'], source_config['casa_scripts']['channels_to_avg'])
        script_parameters = "{0} {1} {2} {3} {4} {5} {6}".format(self._dataset_path, self._output_path,
                                                                 flux_cal_field, phase_cal_field,
                                                                 spw, refant, minsnr)
        self._run(script_path, script_parameters)

    def apply_target_source_calibration(self, flux_cal_field, phase_cal_field, source_config):
        logging.info(Color.HEADER + "Applying Calibration to Target Source..." + Color.ENDC)
        script_path = 'casa_scripts/target_source_calibration.py'
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, self._output_path,
                                                         flux_cal_field, phase_cal_field,
                                                         source_config['field'])
        self._run(script_path, script_parameters)

    def r_flag(self, source):
        source_config = ALL_CONFIGS[source]
        r_flag_config = source_config['r_flag']
        script_path = 'casa_scripts/r_flag.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7}".format(r_flag_config['freqrange'], self._dataset_path,
                                                                     source_config['field'],
                                                                     source_config['spw'],
                                                                     r_flag_config['freqdevscale'],
                                                                     r_flag_config['timedevscale'],
                                                                     r_flag_config['growfreq'],
                                                                     r_flag_config['growtime'])
        logging.info(Color.HEADER + "Running Rflag for flagging in frequency..." + Color.ENDC)
        self._run(script_path, script_parameters)

    def setjy(self, source_id, source_name):
        logging.info(Color.HEADER + 'Running setjy' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        freq_band = "L"
        model_path = "{0}/{1}_{2}.im".format(CASAPY_CONFIG['model_path'], source_name, freq_band)
        script_parameters = "{0} {1} {2}".format(self._dataset_path, source_id, model_path)
        self._run(script_path, script_parameters, CASAPY_CONFIG['path'])

    def split(self, output_path, filters):
        logging.info(Color.HEADER + "Splitting dataset at location {0}".format(output_path) + Color.ENDC)
        script_path = 'casa_scripts/split_dataset.py'
        spw = filters.get("spw", "all")
        width = filters.get("width", 1)
        script_parameters = "{0} {1} {2} {3} {4} {5}".format(self._dataset_path, output_path, filters['field'],
                                                             filters['datacolumn'], width, spw)
        self._run(script_path, script_parameters)

    def _unlock_dataset(self):
        table = casac.casac.table()
        table.open(self._dataset_path)
        table.unlock()

    def _run(self, script, script_parameters=None, casapy_path=CASAPY_CONFIG['path']):
        if not script_parameters: script_parameters = self._dataset_path
        self._unlock_dataset()
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui -c {1} {2}".format(casapy_path, script_full_path, script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        while process.poll() is None:
            time.sleep(1)
