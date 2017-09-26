from sources.source import Source
from configs import config
from continuum_source import ContinuumSource
from helpers import create_dir
from measurement_set import MeasurementSet


class LineSource(Source):
    ID = 0  # line source ID will be always 0

    def __init__(self, measurement_set, parent_source_id):
        self.source_type = 'line'
        self.source_ids = [LineSource.ID]
        self.parent_source_id = parent_source_id
        super(LineSource, self).__init__(measurement_set)

    def apply_calibration(self, mode):
        selfcal_config = config.IMAGING_CONFIGS['cont_image']['self_calibration']
        self.measurement_set.casa_runner.apply_line_calibration(selfcal_config["calmode"], self.parent_source_id, mode)

    def continuum(self, spw, cont_mode):
        continuum_config = config.TARGET_SOURCE_CONFIGS[cont_mode + '_continuum']
        continuum_ms_path, continuum_output_path = self._prepare_output_dir(
            "continuum_{0}_{1}".format(cont_mode, self.parent_source_id))
        width = continuum_config['channel_width']
        self.measurement_set.split(continuum_ms_path,
                                   {'datacolumn': 'data', 'spw': spw, 'width': width,
                                    'channels_to_avg': continuum_config['channels_to_avg']})
        return ContinuumSource(MeasurementSet(continuum_ms_path, continuum_output_path), self.parent_source_id,
                               cont_mode)

    def extend_continuum_flags(self):
        self.measurement_set.casa_runner.extend_continuum_flags()
        scan_ids = self.measurement_set.scan_ids(self.source_ids)
        self.measurement_set.casa_runner.generate_flag_summary("detailed_flagging", scan_ids, self.source_type)

    def create_line_image(self):
        cont_config = config.IMAGING_CONFIGS['cont_image']['self_calibration']
        self.measurement_set.casa_runner.create_line_image(cont_config["calmode"], self.parent_source_id)
