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

    def _get_next_scan_id(self, scan_id, source_id):
        scan_ids = self.measurement_set.scan_ids_for(source_id)
        index = scan_ids.index(scan_id)
        if len(scan_ids) != index + 1:
            return scan_ids[index + 1]

    def _flag_bad_scans(self, polarization, antenna_id, bad_scan_ids, source_id):
        for bad_scan_id in bad_scan_ids:
            if not is_last_element(bad_scan_id, bad_scan_ids):
                next_scan_id = self._get_next_scan_id(bad_scan_id, source_id)
                if next_scan_id in bad_scan_ids:
                    scan_ids_to_flag = range(bad_scan_id, next_scan_id + 1)
                    self.measurement_set.flag_antennas(polarization, scan_ids_to_flag, [antenna_id])

    def flag_bad_antennas_of_phase_cal(self, polarization):
        phase_cal_field = GLOBAL_CONFIG['phase_cal_field']
        completely_bad_antennas = self.measurement_set.get_completely_flagged_antennas(polarization)
        antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, phase_cal_field)

        for completely_bad_antenna in completely_bad_antennas:
            del antennas_with_scans[completely_bad_antenna]

        for antenna_id, bad_scan_ids in antennas_with_scans.iteritems():
            if len(bad_scan_ids) > 1:
                bad_scan_ids.sort()
                self._flag_bad_scans(polarization, antenna_id, bad_scan_ids, phase_cal_field)

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
