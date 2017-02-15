from casa.flag_reasons import BAD_ANTENNA
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from models.antenna_status import AntennaStatus
from report import Report
from sources.source import Source


class PhaseCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'phase_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['phase_cal_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(PhaseCalibrator, self).__init__(measurement_set, self.source_name)

    def flag_antennas(self):
        self.analyse_antennas_on_angular_dispersion()
        self.analyse_antennas_on_closure_phases()
        scan_ids = self.measurement_set.scan_ids_for(self.source_id)
        Report(self.measurement_set.get_antennas()).generate_report(scan_ids)

        def is_bad(state):
            return state.get_R_phase_status() == AntennaStatus.BAD and state.get_closure_phase_status() == AntennaStatus.BAD

        self.measurement_set.flag_bad_antennas(is_bad, self.source_id)
        self.measurement_set.casa_runner.flagdata(BAD_ANTENNA)

    def calibrate(self):
        flux_cal_field = GLOBAL_CONFIG['flux_cal_field']
        self.measurement_set.casa_runner.apply_phase_calibration(flux_cal_field, self.config)
