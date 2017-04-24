from configs import config
from casa.flag_reasons import BAD_ANTENNA_TIME, BAD_BASELINE_TIME
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

    def flagdata(self, reasons, output_path=None):
        if not output_path: output_path = self._output_path
        logging.info(Color.HEADER + "Flagging " + reasons + Color.ENDC)
        script_path = 'casa_scripts/flag.py'
        flag_file = output_path + "/flags.txt"
        script_parameters = "{0} {1} {2}".format(self._dataset_path, flag_file, reasons)
        self._run(script_path, script_parameters)

    def quack(self):
        logging.info(Color.HEADER + "Running quack..." + Color.ENDC)
        script_path = 'casa_scripts/quack.py'
        self._run(script_path)

    def apply_flux_calibration(self, source_config, run_count):
        logger_message = "Applying Flux Calibration"
        if run_count > 1: logger_message += " with bandpass"

        logging.info(Color.HEADER + logger_message + Color.ENDC)
        script_path = 'casa_scripts/flux_calibration.py'
        fields = ",".join(map(str, source_config['fields']))
        refant = config.GLOBAL_CONFIG['refant']
        minsnr = source_config['minsnr']
        spw = "{0}:{1}".format(config.GLOBAL_CONFIG['spw_range'], source_config['channel'])
        script_parameters = "{0} {1} {2} {3} {4} {5} {6}".format(run_count, self._dataset_path,
                                                                 self._output_path,
                                                                 fields, refant, spw, minsnr)
        self._run(script_path, script_parameters)

    def apply_bandpass_calibration(self, source_config):
        logging.info(Color.HEADER + "Running Bandpass Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/bandpass_calibration.py'
        fields = ",".join(map(str, source_config['fields']))
        refant = config.GLOBAL_CONFIG['refant']
        minsnr = source_config['minsnr']
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, self._output_path, fields, refant, minsnr)

        self._run(script_path, script_parameters)

    def apply_phase_calibration(self, flux_cal_field, source_config):
        logging.info(Color.HEADER + "Applying Phase Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/phase_calibration.py'
        phase_cal_fields = ",".join(map(str, source_config['fields']))
        refant = config.GLOBAL_CONFIG['refant']
        minsnr = source_config['minsnr']
        spw = "{0}:{1}".format(config.GLOBAL_CONFIG['spw_range'], source_config['channels_to_avg'])
        script_parameters = "{0} {1} {2} {3} {4} {5} {6}".format(self._dataset_path, self._output_path,
                                                                 flux_cal_field, phase_cal_fields,
                                                                 spw, refant, minsnr)
        self._run(script_path, script_parameters)

    def apply_target_source_calibration(self, source_config):
        logging.info(Color.HEADER + "Applying Calibration to Target Source..." + Color.ENDC)
        flux_cal_fields = ",".join(map(str, config.GLOBAL_CONFIG['flux_cal_fields']))
        phase_cal_fields = ",".join(map(str, config.GLOBAL_CONFIG['phase_cal_fields']))
        script_path = 'casa_scripts/target_source_calibration.py'
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, self._output_path,
                                                         flux_cal_fields, phase_cal_fields,
                                                         source_config['field'])
        self._run(script_path, script_parameters)

    def r_flag(self, source_config):
        auto_flagging_algo = source_config['auto_flagging_algo']
        r_flag_config = auto_flagging_algo['r_flag']
        fields = ",".join(map(str, source_config['fields']))
        script_path = 'casa_scripts/r_flag.py'

        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8}".format(auto_flagging_algo['datacolumn'],
                                                                         auto_flagging_algo['freqrange'],
                                                                         self._dataset_path,
                                                                         fields,
                                                                         config.GLOBAL_CONFIG['spw_range'],
                                                                         r_flag_config['freqdevscale'],
                                                                         r_flag_config['timedevscale'],
                                                                         auto_flagging_algo['growfreq'],
                                                                         auto_flagging_algo['growtime'])
        logging.info(Color.HEADER + "Running Rflag auto-flagging algorithm" + Color.ENDC)
        self._run(script_path, script_parameters)

    def tfcrop(self, source_config):
        auto_flagging_algo = source_config['auto_flagging_algo']
        tf_crop_config = auto_flagging_algo['tf_crop']
        fields = ",".join(map(str, source_config['fields']))
        script_path = 'casa_scripts/tfcrop.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}".format(auto_flagging_algo['datacolumn'],
                                                                                       auto_flagging_algo['freqrange'],
                                                                                       tf_crop_config['maxnpieces'],
                                                                                       tf_crop_config['usewindowstats'],
                                                                                       tf_crop_config['halfwin'],
                                                                                       tf_crop_config['freqcutoff'],
                                                                                       tf_crop_config['timecutoff']
                                                                                       , self._dataset_path,
                                                                                       fields,
                                                                                       config.GLOBAL_CONFIG[
                                                                                           'spw_range'],
                                                                                       auto_flagging_algo['growfreq'],
                                                                                       auto_flagging_algo['growtime']
                                                                                       )
        logging.info(Color.HEADER + "Running Tfcrop auto-flagging algorithm" + Color.ENDC)
        self._run(script_path, script_parameters)

    def setjy(self, source_id, source_name):
        logging.info(Color.HEADER + 'Running setjy' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        freq_band = "L"
        model_path = "{0}/{1}_{2}.im".format(config.CASAPY_CONFIG['model_path'], source_name.split("_")[0], freq_band)
        script_parameters = "{0} {1} {2} {3}".format(config.GLOBAL_CONFIG['spw_range'], self._dataset_path, source_id,
                                                     model_path)
        self._run(script_path, script_parameters)

    def split(self, output_path, filters):
        script_path = 'casa_scripts/split_dataset.py'
        logging.info(Color.HEADER + "Splitting dataset at location {0}".format(output_path) + Color.ENDC)
        spw = filters.get("spw", "all")
        width = filters.get("width", 1)
        field = filters.get("field", 0)
        script_parameters = "{0} {1} {2} {3} {4} {5}".format(self._dataset_path, output_path, field,
                                                             filters['datacolumn'], width, spw)
        self._run(script_path, script_parameters)

    def base_image(self, image_config):
        logging.info(Color.HEADER + "Creating base image for {0}".format(self._dataset_path) + Color.ENDC)
        script_path = 'casa_scripts/base_image.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8}".format(self._dataset_path, self._output_path,
                                                                         image_config['imsize'], image_config['cell'],
                                                                         image_config['robust'],
                                                                         image_config['clean_threshold'],
                                                                         image_config['interactive'],
                                                                         image_config['niter'],
                                                                         image_config['cyclefactor'])

        self._run(script_path, script_parameters)

    def apply_self_calibration(self, self_cal_config, calibration_mode, output_ms_path, output_path):
        logging.info(Color.HEADER + "Applying self calibration for {0}".format(self._dataset_path) + Color.ENDC)
        cal_mode = self_cal_config['calmode']
        channel = 0
        spw = "{0}:{1}".format(config.GLOBAL_CONFIG['spw_range'], channel)
        mask_path = self_cal_config['masking']['mask_path'] if self_cal_config['masking']['mask_path'] else 'None'

        script_path = 'casa_scripts/self_calibration.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} {16} {17} {18} {19}".format(
            self._dataset_path,
            output_path,
            output_ms_path,
            cal_mode[calibration_mode]['solint'],
            config.GLOBAL_CONFIG['refant'],
            self_cal_config['minsnr'],
            self._output_path,
            self_cal_config['imsize'],
            self_cal_config['cell'],
            cal_mode[calibration_mode]['robust'],
            self_cal_config['interactive'],
            self_cal_config['niter'],
            self_cal_config['clean_threshold'],
            self_cal_config['masking']['threshold'],
            mask_path,
            cal_mode['ap']['loop_count'],
            cal_mode['p']['loop_count'],
            self_cal_config['cyclefactor'],
            calibration_mode, spw)

        self._run(script_path, script_parameters)

    def fourier_transform(self, field_name, model_name):
        logging.info(Color.HEADER + "Calculating fourier transform on {0}".format(model_name) + Color.ENDC)
        script_path = 'casa_scripts/fourier_transform.py'
        script_parameters = "{0} {1} {2}".format(self._dataset_path, field_name, model_name)
        self._run(script_path, script_parameters)

    def apply_line_calibration(self, calmode_config):
        logging.info(Color.HEADER + "Applying calibration on Line.." + Color.ENDC)
        script_path = 'casa_scripts/apply_line_calibration.py'
        script_parameters = "{0} {1} {2} {3}".format(self._dataset_path, config.OUTPUT_PATH,
                                                     calmode_config["p"]["loop_count"],
                                                     calmode_config["ap"]["loop_count"])
        self._run(script_path, script_parameters)

    def extend_continuum_flags(self):
        logging.info(Color.HEADER + "Extending continuum flags on line..." + Color.ENDC)
        flag_reasons = "{0},{1}".format(BAD_ANTENNA_TIME, BAD_BASELINE_TIME)
        self.flagdata(flag_reasons, config.OUTPUT_PATH + "/continuum/")

    def create_line_image(self, image_config, model="-"):
        logging.info(Color.HEADER + "Creating line image at {0}".format(self._output_path) + Color.ENDC)

        script_path = 'casa_scripts/create_line_image.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8}".format(
            self._dataset_path,
            self._output_path,
            model,
            image_config['threshold'],
            image_config['imsize'],
            image_config['interactive'],
            image_config['robust'],
            image_config['cell'],
            image_config['niter'])

        self._run(script_path, script_parameters)

    def _unlock_dataset(self):
        table = casac.casac.table()
        table.open(self._dataset_path)
        table.unlock()

    def _run(self, script, script_parameters=None):
        casapy_path = config.CASAPY_CONFIG['path']
        if not script_parameters: script_parameters = self._dataset_path
        self._unlock_dataset()
        logfile = config.OUTPUT_PATH + "/casa.log"
        script_full_path = os.path.realpath(script)
        command = "{0} --nologger --nogui  --logfile {1} -c {2} {3}".format(casapy_path, logfile, script_full_path,
                                                                            script_parameters)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        while process.poll() is None:
            time.sleep(1)
