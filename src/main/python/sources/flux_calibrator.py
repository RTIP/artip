from logger import logger
from configs import config
from sources.source import Source
from terminal_color import Color

class FluxCalibrator(Source):
    def __init__(self, measurement_set):
        self.source_type = 'flux_calibrator'
        self.config = config.ALL_CONFIGS[self.source_type]
        self.source_ids = config.GLOBAL_CONFIGS['flux_cal_fields']
        super(FluxCalibrator, self).__init__(measurement_set)

    def run_setjy(self):
        for source_id in self.source_ids:
            source_name = self.measurement_set.get_field_name_for(source_id)
            self.measurement_set.casa_runner.setjy(source_id, source_name)
        self.measurement_set.reload()

    def extend_flags(self):
        logger.info(Color.HEADER + "Extending flags..." + Color.ENDC)
        self._extend_bad_antennas_across_all_sources()

    def _extend_bad_antennas_across_all_sources(self):
        polarizations = config.GLOBAL_CONFIGS['polarizations']
        for polarization in polarizations:
            scan_ids = self.measurement_set.scan_ids(self.source_ids, polarization)
            antennas_with_scans = self.measurement_set.get_bad_antennas_with_scans_for(polarization, self.source_ids)
            bad_antennas = filter(lambda antenna: len(antennas_with_scans[antenna]) == len(scan_ids),
                                  antennas_with_scans.keys())

            self.measurement_set.flag_antennas(self.flag_file, [polarization], self.measurement_set.scan_ids(), bad_antennas)

    def calibrate(self):
        self.measurement_set.casa_runner.apply_flux_calibration(self.config, 1)
        self.measurement_set.reload()
