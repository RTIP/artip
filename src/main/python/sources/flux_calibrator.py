from casa.flag_reasons import BAD_ANTENNA
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from models.antenna_status import AntennaStatus
from report import Report
from sources.source import Source


class FluxCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'flux_calibration'
        self.config = ALL_CONFIGS[self.source_type]
        self.source_id = GLOBAL_CONFIG['flux_cal_field']
        self.source_name = measurement_set.get_field_name_for(self.source_id)
        super(FluxCalibrator, self).__init__(measurement_set, self.source_name)

    def run_setjy(self):
        self.measurement_set.casa_runner.setjy(self.source_id, self.source_name)

    def flag_antennas(self):
        self.analyse_antennas_on_angular_dispersion()
        self.analyse_antennas_on_closure_phases()

        scan_ids = self.measurement_set.scan_ids_for(self.source_id)
        Report(self.measurement_set.get_antennas()).generate_report(scan_ids)

        def is_bad(state):
            return state.get_R_phase_status() == AntennaStatus.BAD and state.get_closure_phase_status() == AntennaStatus.BAD

        self.measurement_set.flag_bad_antennas(is_bad, self.source_id)
        self._extend_bad_antennas_across_all_sources()
        self.measurement_set.casa_runner.flagdata(BAD_ANTENNA)

    def _extend_bad_antennas_across_all_sources(self):
        polarizations = GLOBAL_CONFIG['polarizations']
        for polarization in polarizations:
            scan_ids = self.measurement_set.scan_ids_for(self.source_id)
            antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, self.source_id)
            bad_antennas = filter(lambda antenna: len(antennas_with_scans[antenna]) == len(scan_ids),
                                  antennas_with_scans.keys())

            self.measurement_set.flag_antennas(polarization, self.measurement_set.scan_ids(), bad_antennas)

    def calibrate(self):
        self.measurement_set.casa_runner.apply_flux_calibration(self.config)
        self.measurement_set.reload()
