from configs import config
from sources.target_source import TargetSource
from measurement_set import MeasurementSet
from helpers import Debugger
from terminal_color import Color
import itertools
from logger import logger


class ContinuumSource(TargetSource):
    def __init__(self, measurement_set, source_id):
        super(ContinuumSource, self).__init__(measurement_set, source_id)
        self.source_type = 'continuum'
        self.source_ids = [0]  # source_id will always be 0
        self.config = config.ALL_CONFIGS["target_source"][self.source_type]

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def _flag_bad_time(self, reason, analyser):
        debugger = Debugger(self.measurement_set)
        polarizations = config.GLOBAL_CONFIG['polarizations']
        scan_ids = self.measurement_set.scan_ids_for(self.source_ids)
        spws = config.GLOBAL_CONFIG['default_spw']
        spw_polarization_scan_product = list(itertools.product(spws, polarizations, scan_ids))
        self._flag_only_once(reason, analyser, spw_polarization_scan_product, debugger)

    def _flag_only_once(self, reason, analyser, spw_polarization_scan_product, debugger):
        bad_time_present = analyser(spw_polarization_scan_product, debugger)
        if bad_time_present:
            logger.info(Color.HEADER + 'Flagging {0} in CASA'.format(reason) + Color.ENDC)
            self.measurement_set.casa_runner.flagdata(reason)
        else:
            logger.info(Color.OKGREEN + 'No {0} Found'.format(reason) + Color.ENDC)

    def self_calibrate(self):
        config = self.config['self_calibration']
        self._base_image()
        self_caled_p = self.apply_self_calibration(config, 'p')
        self_caled_p.attach_model(config, 'p')
        self_caled_p.apply_self_calibration(config, 'ap')

    def apply_self_calibration(self, config, cal_mode):
        ms_path, output_path = self.prepare_output_dir("self_caled_{0}_{1}".format(cal_mode, self.source_id))
        self.measurement_set.casa_runner.apply_self_calibration(config, cal_mode, ms_path, output_path, self.source_id)
        return ContinuumSource(MeasurementSet(ms_path, output_path), self.source_id)

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
