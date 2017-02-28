from configs.config import ALL_CONFIGS
from configs.config import GLOBAL_CONFIG
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from helpers import Debugger
from terminal_color import Color
import itertools
import logging


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set):
        super(ContinuumSource, self).__init__(measurement_set)
        self.source_type = 'continuum'
        self.source_ids = [0]  # source_id will always be 0
        self.config = ALL_CONFIGS["target_source"][self.source_type]

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def _flag_bad_time(self, reason, analyser):
        debugger = Debugger(self.measurement_set)
        polarizations = GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_ids)
        polarization_scan_product = list(itertools.product(polarizations, scan_ids))
        self._flag_only_once(reason, analyser, polarization_scan_product, debugger)

    def _flag_only_once(self, reason, analyser, polarization_scan_product, debugger):
        bad_time_present = analyser(polarization_scan_product, self.config, debugger)
        if bad_time_present:
            logging.info(Color.HEADER + 'Flagging {0} in CASA'.format(reason) + Color.ENDC)
            self.measurement_set.casa_runner.flagdata(reason)
        else:
            logging.info(Color.OKGREEN + 'No {0} Found'.format(reason) + Color.ENDC)

    def self_calibrate(self):
        config = self.config['self_calibration']
        self._base_image()
        self_caled_p = self.apply_self_calibration(config, 'p')
        self_caled_p.attach_model(config, 'p')
        self_caled_p.apply_self_calibration(config, 'ap')

    def apply_self_calibration(self, config, cal_mode):
        ms_path, output_path = self.prepare_output_dir("self_caled_{0}".format(cal_mode))
        self.measurement_set.casa_runner.apply_self_calibration(config, cal_mode, ms_path, output_path)
        return ContinuumSource(MeasurementSet(ms_path, output_path))

    def attach_model(self, self_calibration_config, cal_mode):
        self.measurement_set.casa_runner.fourier_transform(self._source_name(),
                                                           self._image_model(self_calibration_config, cal_mode))

    def _base_image(self):
        self.measurement_set.casa_runner.base_image(self.config['image'])

    def _source_name(self):
        continuum_source_id = 0  # Will be always 0
        return self.measurement_set.get_field_name_for(continuum_source_id)

    def _image_model(self, self_calibration_config, cal_mode):
        image_path = '{0}/self_cal_image'.format(self.measurement_set.get_output_path())
        return "{0}_{1}_{2}.model".format(image_path, cal_mode,
                                          self_calibration_config['calmode'][cal_mode]['loop_count'])
