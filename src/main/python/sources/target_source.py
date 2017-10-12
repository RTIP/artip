from configs import config
from utilities.helpers import is_last_element, create_dir
from source import Source
import numpy
from models.measurement_set import MeasurementSet
from line_source import LineSource


class TargetSource(Source):
    def __init__(self, measurement_set, source_id):
        self.source_type = 'target_source'
        self.config = config.TARGET_SOURCE_CONFIGS
        self.source_ids = [source_id]
        super(TargetSource, self).__init__(measurement_set)

    def calibrate(self):
        self.measurement_set.casa_runner.apply_target_source_calibration(self.source_ids[0])

    def line(self):
        line_ms_path, line_output_path = self._prepare_output_dir("line_{0}".format(self.source_ids[0]))
        self.measurement_set.split(line_ms_path, {'datacolumn': 'corrected', 'field': self.source_ids[0]})
        return LineSource(MeasurementSet(line_ms_path, line_output_path), self.source_ids[0])
