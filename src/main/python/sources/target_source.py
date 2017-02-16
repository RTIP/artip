from configs.config import ALL_CONFIGS, GLOBAL_CONFIG, OUTPUT_PATH
from helpers import is_last_element, create_dir
from sources.source import Source

from measurement_set import MeasurementSet


class TargetSource(Source):
    def __init__(self, measurement_set):
        self.__measurement_set = measurement_set
        self.source_type = 'target_source'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['target_src_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(TargetSource, self).__init__(measurement_set, self.source_name)

    def reduce_data(self):
        self.flag_and_calibrate_in_detail()

    def calibrate(self):
        flux_cal_field = GLOBAL_CONFIG['flux_cal_field']
        phase_cal_field = GLOBAL_CONFIG['phase_cal_field']
        self.measurement_set.casa_runner.apply_target_source_calibration(flux_cal_field, phase_cal_field, self.config)

    def split(self):
        spw = "{0}:{1}".format(self.config["spw"], self.config["channels_for_line"])
        line_ms_path, line_output_path = self.prepare_output_dir("line")
        self.__measurement_set.split(line_ms_path, [self.source_id], [spw], "CORRECTED_DATA")
        return TargetSource(MeasurementSet(line_ms_path, line_output_path))

    def create_continuum(self):
        spw = "{0}:{1}".format(self.config["spw"], self.config["channels_for_line"])
        continuum_ms_path, continuum_output_path = self.prepare_output_dir("continuum")
        self.__measurement_set.split(continuum_ms_path, [self.source_id], spw, "DATA")
        return TargetSource(MeasurementSet(continuum_ms_path))

    def prepare_output_dir(self, new_dir):
        output_path = self.__measurement_set.get_output_path() + "/" + new_dir
        create_dir(output_path)
        ms_path = output_path + "/{0}.ms".format(new_dir)
        return ms_path, output_path
