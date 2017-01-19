from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from casa.flag_reasons import BAD_ANTENNA
from sources.source import Source
from helpers import is_last_element
import logging
from terminal_color import Color


class TargetSource(Source):
    def __init__(self, measurement_set):
        self.source_type = 'target_source'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['target_src_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(TargetSource, self).__init__(measurement_set, self.source_name)

    def flag_antennas(self):
        polarizations = GLOBAL_CONFIG['polarizations']
        for polarization in polarizations:
            self.flag_bad_antennas_of_phase_cal(polarization)
        CasaRunner.flagdata(BAD_ANTENNA)

    def reduce_data(self):
        logging.info(Color.HEADER + "Flagging bad antennas on" + self.source_type + "..." + Color.ENDC)
        self.flag_antennas()

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
                    scans_to_flag = "{0}~{1}".format(bad_scan_id, next_scan_id)
                    self.measurement_set.make_entry_in_flag_file(polarization, scans_to_flag, [antenna_id])

    def flag_bad_antennas_of_phase_cal(self, polarization):
        phase_cal_field = GLOBAL_CONFIG['phase_cal_field']

        antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, phase_cal_field)

        for antenna_id, bad_scan_ids in antennas_with_scans.iteritems():
            if len(bad_scan_ids) > 1:
                bad_scan_ids.sort()
                self._flag_bad_scans(polarization, antenna_id, bad_scan_ids, phase_cal_field)

    def calibrate(self):
        CasaRunner.apply_target_source_calibration(self.source_id)
