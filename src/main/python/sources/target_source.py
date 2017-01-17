from casa.casa_runner import CasaRunner
from configs.config import ALL_CONFIGS, GLOBAL_CONFIG
from casa.flag_reasons import BAD_ANTENNA
from sources.source import Source


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
            bad_antennas = self.get_bad_antennas_for_flux_cal(polarization)

            self.measurement_set.make_entry_in_flag_file(polarization, '', bad_antennas)
            CasaRunner.flagdata(BAD_ANTENNA)

    def get_bad_antennas_for_flux_cal(self, polarization):
        flux_cal_field = GLOBAL_CONFIG['flux_cal_field']
        scan_ids_count = len(self.measurement_set.scan_ids_for(flux_cal_field))
        antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, flux_cal_field)
        return filter(lambda antenna: len(antennas_with_scans[antenna]) == scan_ids_count, antennas_with_scans.keys())

    def calibrate(self):
        CasaRunner.apply_target_source_calibration(self.source_id)
