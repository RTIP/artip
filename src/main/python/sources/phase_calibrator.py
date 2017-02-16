from casa.flag_reasons import BAD_ANTENNA
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from models.antenna_status import AntennaStatus
from report import Report
from sources.source import Source
from helpers import is_last_element


class PhaseCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'phase_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['phase_cal_field']
        super(PhaseCalibrator, self).__init__(measurement_set)

    def flag_antennas(self):
        self.analyse_antennas_on_angular_dispersion()
        self.analyse_antennas_on_closure_phases()
        scan_ids = self.measurement_set.scan_ids_for(self.source_id)
        Report(self.measurement_set.get_antennas()).generate_report(scan_ids)

        def is_bad(state):
            return state.get_R_phase_status() == AntennaStatus.BAD and state.get_closure_phase_status() == AntennaStatus.BAD

        self.measurement_set.flag_bad_antennas(is_bad, self.source_id)
        self._extend_bad_antennas_on_target_source()
        self.measurement_set.casa_runner.flagdata(BAD_ANTENNA)

    def calibrate(self):
        flux_cal_field = GLOBAL_CONFIG['flux_cal_field']
        self.measurement_set.casa_runner.apply_phase_calibration(flux_cal_field, self.config)

    def _extend_bad_antennas_on_target_source(self):
        polarizations = GLOBAL_CONFIG['polarizations']
        for polarization in polarizations:
            phase_cal_field = GLOBAL_CONFIG['phase_cal_field']
            completely_bad_antennas = self.measurement_set.get_completely_flagged_antennas(polarization)
            antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, phase_cal_field)

            for completely_bad_antenna in completely_bad_antennas:
                del antennas_with_scans[completely_bad_antenna]

            for antenna_id, bad_scan_ids in antennas_with_scans.iteritems():
                if len(bad_scan_ids) > 1:
                    bad_scan_ids.sort()
                    self._flag_bad_scans(polarization, antenna_id, bad_scan_ids, phase_cal_field)

    def _flag_bad_scans(self, polarization, antenna_id, bad_scan_ids, source_id):
        for bad_scan_id in bad_scan_ids:
            if not is_last_element(bad_scan_id, bad_scan_ids):
                next_scan_id = self._get_next_scan_id(bad_scan_id, source_id)
                if next_scan_id in bad_scan_ids:
                    scan_ids_to_flag = range(bad_scan_id, next_scan_id + 1)
                    self.measurement_set.flag_antennas(polarization, scan_ids_to_flag, [antenna_id])

    def _get_next_scan_id(self, scan_id, source_id):
        scan_ids = self.measurement_set.scan_ids_for(source_id)
        index = scan_ids.index(scan_id)
        if len(scan_ids) != index + 1:
            return scan_ids[index + 1]
