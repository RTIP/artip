from configs import config
from casa.flag_reasons import BAD_ANTENNA_TIME, BAD_BASELINE_TIME
import os
import platform
import subprocess
import casac
from logger import logger
from terminal_color import Color
from helpers import format_spw_with_channels, create_dir
from watchdog.observers import Observer
from log_event_handler import LogEventHandler
from named_tuples import CalibParams


class CasaRunner:
    def __init__(self, dataset_path, output_path):
        self._output_path = output_path
        self._dataset_path = dataset_path

    def _observe_imaging_logs(func):
        def wrapper(*args, **kwargs):
            observer = Observer()
            observer.schedule(LogEventHandler.imaging_log_handler(),
                              path=config.OUTPUT_PATH, recursive=False)
            observer.start()
            func(*args, **kwargs)
            observer.stop()

        return wrapper

    def flagdata(self, flag_file, reasons="any"):
        logger.info(Color.HEADER + "Flagging " + reasons + " reasons" + Color.ENDC)
        script_path = 'casa_scripts/flag.py'
        script_parameters = "{0} {1} {2}".format(self._dataset_path, flag_file, reasons)
        self._run(script_path, script_parameters, subprocess.PIPE)

    def quack(self):
        logger.info(Color.HEADER + "Running quack..." + Color.ENDC)
        script_path = 'casa_scripts/quack.py'
        show_percentage = config.PIPELINE_CONFIGS['flagging_percentage']
        script_parameters = "{0} {1}".format(self._dataset_path, show_percentage)
        self._run(script_path, script_parameters, stdout=subprocess.PIPE)

    def generate_flag_summary(self, flagging_type, scan_list, source_type="All"):
        script_path = 'casa_scripts/flag_summary.py'
        scans = ','.join(str(e) for e in scan_list)
        path = "{0}/json_store".format(config.OUTPUT_PATH)
        create_dir(path)
        polarizations = ",".join(config.GLOBAL_CONFIGS['polarizations'])
        script_parameters = "{0} {1} {2} {3} {4} {5}".format(polarizations, self._dataset_path,
                                                             path,
                                                             flagging_type, scans, source_type)
        self._run(script_path, script_parameters)

    def apply_flux_calibration(self, source_config, run_count):
        logger_message = "Applying Flux Calibration"
        if run_count > 1: logger_message += " with bandpass"
        calib_params = CalibParams(*config.CALIBRATION_CONFIGS['flux_calibrator']['calib_params'])
        logger.info(Color.HEADER + logger_message + Color.ENDC)
        script_path = 'casa_scripts/flux_calibration.py'
        fields = ",".join(map(str, config.GLOBAL_CONFIGS['flux_cal_fields']))
        refant = config.GLOBAL_CONFIGS['refant']
        spw = format_spw_with_channels(config.GLOBAL_CONFIGS['spw_range'], calib_params.channel)
        script_parameters = "{0} {1} {2} {3} {4} {5} {6}".format(run_count, self._dataset_path,
                                                                 self._output_path,
                                                                 fields, refant, spw, calib_params.minsnr)
        self._run(script_path, script_parameters)

    def apply_bandpass_calibration(self, source_config):
        phase_calib_params = CalibParams(None, None, source_config['phase_calib_params'][0],
                                         source_config['phase_calib_params'][1])
        logger.info(Color.HEADER + "Running Bandpass Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/bandpass_calibration.py'
        fields = ",".join(map(str, config.GLOBAL_CONFIGS['flux_cal_fields']))
        refant = config.GLOBAL_CONFIGS['refant']
        script_parameters = "{0} {1} {2} {3} {4} {5} {6}".format(self._dataset_path, self._output_path, fields, refant,
                                                                 source_config['bpcal_solint'],
                                                                 phase_calib_params.minsnr, phase_calib_params.solint)

        self._run(script_path, script_parameters)

    def apply_phase_calibration(self, flux_cal_field, source_config):
        calib_params = CalibParams(*source_config['calib_params'])
        logger.info(Color.HEADER + "Applying Phase Calibration..." + Color.ENDC)
        script_path = 'casa_scripts/phase_calibration.py'
        phase_cal_fields = ",".join(map(str, config.GLOBAL_CONFIGS['phase_cal_fields']))
        refant = config.GLOBAL_CONFIGS['refant']
        spw = format_spw_with_channels(config.GLOBAL_CONFIGS['spw_range'], source_config['channels_to_avg'])
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7}".format(self._dataset_path, self._output_path,
                                                                     flux_cal_field, phase_cal_fields,
                                                                     spw, refant, calib_params.minsnr,
                                                                     calib_params.solint)
        self._run(script_path, script_parameters)

    def apply_target_source_calibration(self, source_id):
        logger.info(Color.HEADER + "Applying Calibration to Target Source..." + Color.ENDC)
        flux_cal_fields = ",".join(map(str, config.GLOBAL_CONFIGS['flux_cal_fields']))
        phase_cal_fields = ",".join(map(str, config.GLOBAL_CONFIGS['target_phase_src_map'][source_id]))
        script_path = 'casa_scripts/target_source_calibration.py'
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, self._output_path,
                                                         flux_cal_fields, phase_cal_fields,
                                                         source_id)
        self._run(script_path, script_parameters)

    def r_flag(self, source_type, source_ids):
        script_path = 'casa_scripts/r_flag.py'
        source_ids = ','.join([str(source_id) for source_id in source_ids])
        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, source_type, source_ids, config.CONFIG_PATH,
                                                     config.GLOBAL_CONFIGS['spw_range'])
        logger.info(Color.HEADER + "Running Rflag auto-flagging algorithm" + Color.ENDC)
        self._run(script_path, script_parameters)

    def tfcrop(self, source_type, source_ids):
        script_path = 'casa_scripts/tfcrop.py'
        source_ids = ','.join([str(source_id) for source_id in source_ids])

        script_parameters = "{0} {1} {2} {3} {4}".format(self._dataset_path, source_type, source_ids, config.CONFIG_PATH,
                                                     config.GLOBAL_CONFIGS['spw_range'])
        logger.info(Color.HEADER + "Running Tfcrop auto-flagging algorithm" + Color.ENDC)
        self._run(script_path, script_parameters)

    def setjy(self, source_id, source_name):
        logger.info(Color.HEADER + 'Running setjy' + Color.ENDC)
        script_path = 'casa_scripts/setjy.py'
        freq_band = "L"
        model_path = "{0}/{1}_{2}.im".format(config.CASA_CONFIGS['casa'][platform.system()]['model_path'],
                                             source_name.split("_")[0], freq_band)
        script_parameters = "{0} {1} {2} {3}".format(config.GLOBAL_CONFIGS['spw_range'], self._dataset_path, source_id,
                                                     model_path)
        self._run(script_path, script_parameters)

    def split(self, output_path, filters):
        script_path = 'casa_scripts/split_dataset.py'
        logger.info(Color.HEADER + "Splitting dataset at location {0}".format(output_path) + Color.ENDC)
        spw = filters.get("spw", "all")
        width = filters.get("width", '1')
        field = filters.get("field", 0)

        if spw != "all":
            spw = format_spw_with_channels(spw, filters.get("channels_to_avg", ''))

        script_parameters = "{0} {1} {2} {3} {4} {5}".format(self._dataset_path, output_path, field,
                                                             filters['datacolumn'], width, spw)
        self._run(script_path, script_parameters)

    @_observe_imaging_logs
    def base_image(self):
        logger.info(Color.HEADER + "Creating base image for {0}".format(self._dataset_path) + Color.ENDC)
        script_path = 'casa_scripts/base_image.py'
        script_parameters = "{0} {1} {2}".format(self._dataset_path, self._output_path, config.CONFIG_PATH)
        self._run(script_path, script_parameters)

    @_observe_imaging_logs
    def apply_self_calibration(self, selfcal_config, calibration_mode, output_ms_path, output_path, spw):
        logger.info(Color.HEADER + "Applying self calibration for {0}".format(self._dataset_path) + Color.ENDC)
        cal_mode = selfcal_config['calmode']
        mask_path = selfcal_config['masking']['mask_path'] if selfcal_config['masking']['mask_path'] else 'None'

        script_path = 'casa_scripts/self_calibration.py'
        script_parameters = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} " \
                            "{14} {15} {16} {17} {18}".format(config.CONFIG_PATH,
                                                              self._dataset_path,
                                                              output_path,
                                                              output_ms_path,
                                                              cal_mode[calibration_mode]['solint'],
                                                              config.GLOBAL_CONFIGS['refant'],
                                                              selfcal_config['minsnr'],
                                                              self._output_path,
                                                              cal_mode[calibration_mode]['applymode'],
                                                              selfcal_config['masking']['threshold'],
                                                              selfcal_config['masking']['bmask']['bottom_left_corner'][
                                                                  'x_coordinate'],
                                                              selfcal_config['masking']['bmask']['bottom_left_corner'][
                                                                  'y_coordinate'],
                                                              selfcal_config['masking']['bmask']['top_right_corner'][
                                                                  'x_coordinate'],
                                                              selfcal_config['masking']['bmask']['top_right_corner'][
                                                                  'y_coordinate'],
                                                              mask_path,
                                                              cal_mode['ap']['loop_count'],
                                                              cal_mode['p']['loop_count'],
                                                              calibration_mode,
                                                              spw)

        self._run(script_path, script_parameters)

    def fourier_transform(self, field_name, cal_mode, spw_range, loop_count):
        logger.info(Color.HEADER + "Calculating fourier transform on {0}".format(field_name) + Color.ENDC)
        script_path = 'casa_scripts/fourier_transform.py'
        script_parameters = "{0} {1} {2} {3} {4} {5}".format(spw_range, self._output_path, cal_mode, loop_count,
                                                             self._dataset_path,
                                                             field_name)

        self._run(script_path, script_parameters)

    def apply_line_calibration(self, calmode_config, parent_source_id, mode):
        logger.info(Color.HEADER + "Applying calibration on Line.." + Color.ENDC)
        script_path = 'casa_scripts/apply_line_calibration.py'
        p_loop_count = calmode_config["p"]["loop_count"]
        ap_loop_count = calmode_config["ap"]["loop_count"]
        p_table = '{0}/self_caled_p_{1}_{2}/p_selfcaltable_{3}.gcal'.format(config.OUTPUT_PATH, mode, parent_source_id,
                                                                            p_loop_count)
        ap_table = '{0}/self_caled_ap_{1}_{2}/ap_selfcaltable_{3}.gcal'.format(config.OUTPUT_PATH, mode, parent_source_id,
                                                                               ap_loop_count)
        script_parameters = "{0} {1} {2} {3} {4}".format(p_loop_count, ap_loop_count, ap_table, p_table,
                                                         self._dataset_path)
        self._run(script_path, script_parameters)

    def extend_continuum_flags(self):
        logger.info(Color.HEADER + "Extending continuum flags on line..." + Color.ENDC)
        flag_reasons = "{0},{1}".format(BAD_ANTENNA_TIME, BAD_BASELINE_TIME)
        flag_file = "{0}/flags_continuum.txt".format(config.OUTPUT_PATH)
        if os.path.exists(flag_file):
            self.flagdata(flag_file, flag_reasons)

    def create_line_image(self, calmode_config, parent_source_id):
        logger.info(Color.HEADER + "Creating line image at {0}".format(self._output_path) + Color.ENDC)
        script_path = 'casa_scripts/create_line_image.py'
        cont_mode = 'ref'
        continuum_image_model = self._last_continuum_image_model(calmode_config, parent_source_id, cont_mode)
        script_parameters = "{0} {1} {2} {3} {4}".format(
            config.GLOBAL_CONFIGS['spw_range'],
            self._dataset_path,
            self._output_path,
            continuum_image_model,
            config.CONFIG_PATH)
        self._run(script_path, script_parameters)

    def _last_continuum_image_model(self, calmode_config, parent_source_id, cont_mode_to_subtract):
        p_loop_count = calmode_config["p"]["loop_count"]
        ap_loop_count = calmode_config["ap"]["loop_count"]
        if ap_loop_count == 0:
            return '{0}/self_caled_p_{1}_{2}/self_cal_image_p_{3}.model'.format(config.OUTPUT_PATH,
                                                                                cont_mode_to_subtract, parent_source_id,
                                                                                p_loop_count)
        else:
            return '{0}/self_caled_ap_{1}_{2}/self_cal_image_ap_{3}.model'.format(config.OUTPUT_PATH,
                                                                                  cont_mode_to_subtract, parent_source_id,
                                                                                  ap_loop_count)

    def _unlock_dataset(self):
        table = casac.casac.table()
        table.open(self._dataset_path)
        table.unlock()

    def _form_casa_command(self, script, script_parameters):
        casa_path = config.CASA_CONFIGS['casa'][platform.system()]['path']
        logfile = config.OUTPUT_PATH + "/casa.log"
        script_full_path = os.path.realpath(script)
        casa_command = "{0} --nologger --nogui  --logfile {1} -c {2} {3}" \
            .format(casa_path, logfile, script_full_path, script_parameters)
        return casa_command

    def _form_mpi_command(self, script, script_parameters):
        mpi_config = config.CASA_CONFIGS['mpicasa']
        mpi_command = "mpicasa -n {0}".format(mpi_config['n'])
        if mpi_config['hostfile']:
            mpi_command += " --hostfile {0} ".format(mpi_config['hostfile'])

        mpi_command += " --mca btl_tcp_if_include {0} --mca oob_tcp_if_include {1}  " \
            .format(mpi_config['mca']['btl_tcp_if_include'],
                    mpi_config['mca']['oob_tcp_if_include'])

        casa_command = self._form_casa_command(script, script_parameters)
        return mpi_command + casa_command

    def _run(self, script, script_parameters=None, stdout=None):
        casa_output_file = config.OUTPUT_PATH + "/casa_output.txt"

        if not stdout: stdout = file(casa_output_file, 'a+')
        if not script_parameters: script_parameters = self._dataset_path
        self._unlock_dataset()

        if config.CASA_CONFIGS['is_parallel']:
            command = self._form_mpi_command(script, script_parameters)
        else:
            command = self._form_casa_command(script, script_parameters)

        logger.debug("Executing command -> " + command)
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout,
                                stderr=subprocess.PIPE,
                                shell=True)
        proc.wait()
        return proc
