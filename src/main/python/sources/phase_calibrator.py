from logger import logger
from configs import config
from sources.source import Source
from helpers import is_last_element
from terminal_color import Color

class PhaseCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'phase_calibrator'
        self.config = config.ALL_CONFIGS[self.source_type]
        self.source_ids = config.GLOBAL_CONFIG['phase_cal_fields']
        super(PhaseCalibrator, self).__init__(measurement_set)

    def extend_flags(self):
        logger.info(Color.HEADER + "Extending flags..." + Color.ENDC)
        self._extend_bad_antennas_on_target_source()

    def calibrate(self):
        flux_cal_fields = ",".join(map(str, config.GLOBAL_CONFIG['flux_cal_fields']))
        self.measurement_set.casa_runner.apply_phase_calibration(flux_cal_fields, self.config)

    def _extend_bad_antennas_on_target_source(self):
        polarizations = config.GLOBAL_CONFIG['polarizations']
        for polarization in polarizations:
            phase_cal_fields = config.GLOBAL_CONFIG['phase_cal_fields']
            completely_bad_antennas = self.measurement_set.get_completely_flagged_antennas(polarization)
            antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, phase_cal_fields)

            for completely_bad_antenna in completely_bad_antennas:
                del antennas_with_scans[completely_bad_antenna]

            for antenna_id, bad_scan_ids in antennas_with_scans.iteritems():
                if len(bad_scan_ids) > 1:
                    bad_scan_ids.sort()
                    self._flag_bad_scans(polarization, antenna_id, bad_scan_ids, phase_cal_fields)

    def _flag_bad_scans(self, polarization, antenna_id, bad_scan_ids, source_ids):
        for bad_scan_id in bad_scan_ids:
            if not is_last_element(bad_scan_id, bad_scan_ids):
                next_scan_id = self._get_next_scan_id(bad_scan_id, source_ids, polarization)
                if next_scan_id in bad_scan_ids:
                    scan_ids_to_flag = range(bad_scan_id, next_scan_id + 1)
                    self.measurement_set.flag_antennas([polarization], scan_ids_to_flag, [antenna_id])

    def _get_next_scan_id(self, scan_id, source_ids, polarization):
        scan_ids = self.measurement_set.scan_ids(source_ids, polarization)
        index = scan_ids.index(scan_id)
        if len(scan_ids) != index + 1:
            return scan_ids[index + 1]
