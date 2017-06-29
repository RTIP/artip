import casac
import itertools
import numpy
from datetime import datetime, timedelta
from itertools import product

from casa.casa_runner import CasaRunner
from casa.flag_reasons import BAD_ANTENNA, BAD_ANTENNA_TIME, BAD_BASELINE_TIME
from casa.flag_recorder import FlagRecorder
from configs import config
from configs import pipeline_config
from models.antenna import Antenna
from models.antenna_state import AntennaState
from models.phase_set import PhaseSet


class MeasurementSet:
    def __init__(self, dataset_path, output_path):
        self._dataset_path = dataset_path
        self._output_path = output_path
        self.casa_runner = CasaRunner(dataset_path, output_path)
        self.flag_recorder = FlagRecorder(output_path + "/flags.txt")
        self._ms = casac.casac.ms()
        self._ms.open(dataset_path)
        self._antennas = self.create_antennas()
        self.flagged_antennas = self._initialize_flag_data()
        self._register_known_bad_antennas()

    def __del__(self):
        self._ms.close()

    def get_dataset_path(self):
        return self._dataset_path

    def get_output_path(self):
        return self._output_path

    def _initialize_flag_data(self):
        flag_data = {
            polarization: {scan_id: set() for scan_id in self.scan_ids()} for
            polarization in
            config.GLOBAL_CONFIG['polarizations']}
        return flag_data

    def quack(self):
        self.casa_runner.quack()

    def _filter(self, spw, channel, polarization, filters={}):
        self._ms.selectinit(reset=True)
        self._ms.msselect({"spw": spw})
        self._ms.selectpolarization(polarization)
        self._ms.selectchannel(**channel)
        if filters: self._ms.select(filters)

    def reload(self):
        self._ms.close()
        self._ms.open(self._dataset_path)

    def get_data(self, spw, channel, polarization, filters, selection_params, ifraxis=False):
        self._filter(spw, channel, polarization, filters)
        data_items = self._ms.getdata(selection_params, ifraxis=ifraxis)
        return data_items

    def get_phase_data(self, channel, polarization, filters={}):  # To be removed
        return PhaseSet(self.get_data("0", channel, polarization, filters, ['phase'])['phase'][0][0])

    def get_field_name_for(self, field_id):
        return self._ms.metadata().fieldnames()[field_id]

    def scan_ids_for(self, source_ids):
        scan_ids = reduce(lambda scan_ids, source_id:
                          scan_ids + list(self._ms.metadata().scansforfield(source_id)),
                          source_ids, [])
        return map(lambda scan_id: int(scan_id), scan_ids)

    def baselines_for(self, antenna, polarization, scan_id):
        antennas = list(self.antennas(polarization, scan_id))
        antennas.remove(antenna)
        baselines = list(itertools.product(antennas, [antenna]))

        def sort_antennas(baseline):
            sorted_baseline = tuple(sorted(list(baseline), key=lambda antenna: antenna.id))
            return sorted_baseline

        return map(sort_antennas, baselines)

    def create_antennas(self):
        first_scan_id = self._ms.metadata().scannumbers()[0]  # since antenna ids will be constant for all the scans
        antenna_ids = self._ms.metadata().antennasforscan(first_scan_id).tolist()
        antennas = map(lambda id: Antenna(id), antenna_ids)
        scan_ids = self.scan_ids()
        product_pol_scan_ant = itertools.product(config.GLOBAL_CONFIG['polarizations'], scan_ids, antennas)

        for polarization, scan_id, antenna in product_pol_scan_ant:
            antennaState = AntennaState(antenna.id, polarization, scan_id)
            antenna.add_state(antennaState)

        return antennas

    def antenna_ids(self, polarization, scan_id):
        return map(lambda antenna: antenna.id, self.antennas(polarization, scan_id))

    def get_antenna_by_id(self, id):
        return filter(lambda antenna: antenna.id == id, self.antennas())[0]

    def antennas(self, polarization=None, scan_id=None):
        if not (polarization or scan_id):
            return self._antennas
        return filter(lambda antenna: antenna.id not in self.flagged_antennas[polarization][scan_id], self._antennas)

    def antenna_count(self):
        return len(self._antennas)

    def scan_ids(self):
        return self._ms.metadata().scannumbers()

    def timesforscan(self, scan_id):
        quanta = casac.casac.quanta()
        times_with_second = map(lambda time: str(time) + 's', self._ms.metadata().timesforscan(scan_id))
        return numpy.array(
            map(lambda time: quanta.time(quanta.quantity(time), form='ymd'), times_with_second)).flatten()

    def get_completely_flagged_antennas(self, polarization):
        return list(set.intersection(*self.flagged_antennas[polarization].values()))

    def make_entry_in_flag_file(self, polarizations, scan_ids, antenna_ids):
        if antenna_ids:
            self.flag_recorder.mark_entry(
                {'mode': 'manual', 'antenna': ','.join(map(str, antenna_ids)),
                 'reason': BAD_ANTENNA, 'correlation': ','.join(map(str, polarizations)),
                 'scan': ','.join(map(str, scan_ids))})

    def flag_antennas(self, polarizations, scan_ids, antenna_ids):
        self.make_entry_in_flag_file(polarizations, scan_ids, antenna_ids)
        for polarization, scan_id in product(polarizations, scan_ids):
            self.flagged_antennas[polarization][scan_id] = self.flagged_antennas[polarization][scan_id].union(
                set(antenna_ids))

    def flag_bad_antennas(self, sources):
        for antenna in self._antennas:
            for state in antenna.get_states(self.scan_ids_for(sources)):
                if state.scan_id in self.scan_ids() and state.is_bad():
                    self.flag_antennas([state.polarization], [state.scan_id], [antenna.id])

    def _get_timerange_for_flagging(self, timerange):
        datetime_format = '%Y/%m/%d/%H:%M:%S'
        time_delta = timedelta(seconds=1)
        start = datetime.strptime(timerange[0], datetime_format)
        end = datetime.strptime(timerange[1], datetime_format)
        start_with_delta = datetime.strftime(start - time_delta, datetime_format)
        end_with_delta = datetime.strftime(end + time_delta, datetime_format)
        return start_with_delta, end_with_delta

    def flag_bad_antenna_time(self, polarization, scan_id, antenna_id, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        self.flag_recorder.mark_entry(
            {'mode': 'manual', 'antenna': antenna_id, 'reason': BAD_ANTENNA_TIME, 'correlation': polarization,
             'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def flag_bad_baseline_time(self, polarization, scan_id, baseline, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        self.flag_recorder.mark_entry(
            {'mode': 'manual', 'antenna': str(baseline), 'reason': BAD_BASELINE_TIME, 'correlation': polarization,
             'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def get_bad_antennas_with_scans_for(self, polarization, source_id):
        scan_ids = self.scan_ids_for(source_id)
        bad_antennas_with_scans = {}
        for scan_id in scan_ids:
            bad_antennas = self.flagged_antennas[polarization][scan_id]
            for antenna in bad_antennas:
                if not antenna in bad_antennas_with_scans: bad_antennas_with_scans[antenna] = []
                bad_antennas_with_scans[antenna].append(scan_id)
        return bad_antennas_with_scans

    def split(self, output_ms, filters):
        self.casa_runner.split(output_ms, filters)

    def _register_known_bad_antennas(self):
        known_bad_antennas = pipeline_config.PIPELINE_CONFIGS['known_bad_antennas']
        for known_bad_data in known_bad_antennas:
            filtered_scan_ids = list(set(self.scan_ids()).intersection(known_bad_data['scan_ids']))
            self.flag_antennas(known_bad_data['polarizations'], filtered_scan_ids,
                               known_bad_data['antennas'])
