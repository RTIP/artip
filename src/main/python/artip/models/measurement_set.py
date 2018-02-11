import casac
import itertools
import numpy
from datetime import datetime, timedelta
from itertools import product
from artip.configs import config
from artip.models.antenna import Antenna
from artip.models.antenna_state import AntennaState
from artip.models.baseline import Baseline
from artip.models.phase_set import PhaseSet
from artip.models.visibility_data import VisibilityData
from artip.casa.casa_runner import CasaRunner
from artip.casa.flag_reasons import BAD_ANTENNA, BAD_ANTENNA_TIME, BAD_BASELINE_TIME, BAD_TIME
from artip.casa.flag_recorder import FlagRecorder

class MeasurementSet:
    def __init__(self, dataset_path, output_path):
        self._dataset_path = dataset_path
        self.output_path = output_path
        self.casa_runner = CasaRunner(dataset_path, output_path)
        self.flag_recorder = FlagRecorder()
        self._casac = casac.casac
        self._allow_logs_above_warning_level()
        self._ms = self._casac.ms()
        self._ms.open(dataset_path)
        self._all_antenna_ids = self._all_antenna_ids()
        self.flagged_antennas = self._initialize_flag_data()
        self._antennas = self.create_antennas()

    def _allow_logs_above_warning_level(self):
        sink = self._casac.logsink()
        sink.showconsole(True)
        sink.setglobal(True)
        sink.filter('WARN')

    def __del__(self):
        self._ms.close()

    def get_dataset_path(self):
        return self._dataset_path

    def get_output_path(self):
        return self.output_path

    def _initialize_flag_data(self):
        flag_data = {
            polarization: {scan_id: set() for scan_id in self.scan_ids()} for
            polarization in
            config.GLOBAL_CONFIGS['polarizations']}
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

    def create_antennas(self):
        first_scan_id = self._ms.metadata().scannumbers()[0]
        antenna_ids = self._ms.metadata().antennasforscan(first_scan_id).tolist()
        antennas = map(lambda id: Antenna(id), antenna_ids)
        product_pol_scan_ant = []

        for polarization in config.GLOBAL_CONFIGS['polarizations']:
            scan_ids = self.scan_ids(polarization=polarization)
            product_pol_scan_ant += list(itertools.product([polarization], scan_ids, antennas))

        for polarization, scan_id, antenna in product_pol_scan_ant:
            antennaState = AntennaState(antenna.id, polarization, scan_id)
            antenna.add_state(antennaState)

        return antennas

    def _all_antenna_ids(self):
        first_scan_id = self._ms.metadata().scannumbers()[0]
        return self._ms.metadata().antennasforscan(first_scan_id).tolist()

    def antenna_ids(self, polarization=None, scan_id=None):
        return map(lambda antenna: antenna.id, self.antennas(polarization, scan_id))

    def baselines(self, polarization=None, scan_id=None):
        antennaids = self.antenna_ids(polarization, scan_id)

        baselines = [Baseline(antenna1, antenna2)
                     for antenna1, antenna2 in itertools.product(antennaids, antennaids)
                     if antenna1 < antenna2]

        return baselines

    def get_antenna_by_id(self, id):
        return filter(lambda antenna: antenna.id == id, self.antennas())[0]

    def antennas(self, polarization=None, scan_id=None):
        if not (polarization or scan_id):
            return self._antennas
        return filter(lambda antenna: antenna.id not in self.flagged_antennas[polarization][scan_id], self._antennas)

    def get_data(self, spw, channel, polarization, filters, selection_params):
        ifraxis = True  # This will always inserts a default value for the missing rows
        self._filter(spw, channel, polarization, filters)
        data_items = self._ms.getdata(selection_params, ifraxis=ifraxis)
        return VisibilityData(data_items)

    def get_phase_data(self, channel, polarization, filters={}):  # To be removed
        return PhaseSet(self.get_data("0", channel, polarization, filters, ['phase'])['phase'][0][0])

    def get_field_name_for(self, field_id):
        return self._ms.metadata().fieldnames()[field_id]

    def source_ids(self):
        return self._ms.metadata().fieldsforspw(int(config.GLOBAL_CONFIGS['default_spw']))

    def _all_scan_ids(self, source_id=None):
        if source_id is None:
            scan_ids = list(self._ms.metadata().scannumbers())
        else:
            scan_ids = self._ms.metadata().scansforfield(source_id)

        return map(lambda scan_id: int(scan_id), scan_ids)

    def _get_unflagged_scan_ids_for(self, source_id, polarization):
        antenna_ids = set(self._all_antenna_ids)

        def _is_flagged(scan_id, polarization):
            if not polarization: return False
            return set(self.flagged_antennas[polarization][scan_id]) == antenna_ids

        return filter(lambda scan_id: not _is_flagged(scan_id, polarization),
                      self._all_scan_ids(source_id))

    def scan_ids(self, source_ids=None, polarization=None):
        if not source_ids: source_ids = self.source_ids()
        scan_ids = []

        for source_id in source_ids:
            scan_ids += self._get_unflagged_scan_ids_for(source_id, polarization)

        return scan_ids

    def baselines_for(self, antenna, polarization, scan_id):
        antennas = list(self.antennas(polarization, scan_id))
        antennas.remove(antenna)
        baselines = list(itertools.product(antennas, [antenna]))

        def sort_antennas(baseline):
            sorted_baseline = tuple(sorted(list(baseline), key=lambda antenna: antenna.id))
            return sorted_baseline

        return map(sort_antennas, baselines)

    def antenna_count(self, polarization, scan_id):
        return len(self.antennas(polarization, scan_id))

    def timesforscan(self, scan_id, formatted=True):
        times = self._ms.metadata().timesforscan(scan_id)
        if not formatted: return times
        quanta = self._casac.quanta()
        times_with_second = map(lambda time: str(time) + 's', times)
        return numpy.array(
            map(lambda time: quanta.time(quanta.quantity(time), form='ymd'), times_with_second)).flatten()

    def get_completely_flagged_antennas(self, polarization):
        return list(set.intersection(*self.flagged_antennas[polarization].values()))

    def make_entry_in_flag_file(self, flag_file, polarizations, scan_ids, antenna_ids):
        if antenna_ids:
            self.flag_recorder.mark_entry(flag_file,
                                          {'mode': 'manual', 'antenna': ','.join(map(str, antenna_ids)),
                                           'reason': BAD_ANTENNA, 'correlation': ','.join(map(str, polarizations)),
                                           'scan': ','.join(map(str, scan_ids))})

    def flag_antennas(self, flag_file, polarizations, scan_ids, antenna_ids):
        self.make_entry_in_flag_file(flag_file, polarizations, scan_ids, antenna_ids)
        for polarization, scan_id in product(polarizations, scan_ids):
            self.flagged_antennas[polarization][scan_id] = self.flagged_antennas[polarization][scan_id].union(
                set(antenna_ids))

    def flag_bad_antennas(self, flag_file, sources):
        source_scan_ids = self.scan_ids(sources)
        all_scan_ids = self.scan_ids()
        for antenna in self._antennas:
            for state in antenna.get_states(source_scan_ids):
                if state.scan_id in all_scan_ids and state.is_bad():
                    self.flag_antennas(flag_file, [state.polarization], [state.scan_id], [antenna.id])

    def _get_timerange_for_flagging(self, timerange):
        datetime_format = '%Y/%m/%d/%H:%M:%S'
        time_delta = timedelta(seconds=1)
        start = datetime.strptime(timerange[0], datetime_format)
        end = datetime.strptime(timerange[1], datetime_format)
        start_with_delta = datetime.strftime(start - time_delta, datetime_format)
        end_with_delta = datetime.strftime(end + time_delta, datetime_format)
        return start_with_delta, end_with_delta

    def flag_bad_time(self, flag_file, polarization, scan_id, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        self.flag_recorder.mark_entry(flag_file,
                                      {'mode': 'manual', 'reason': BAD_TIME, 'correlation': polarization,
                                       'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def flag_bad_antenna_time(self, flag_file, polarization, scan_id, antenna_id, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        self.flag_recorder.mark_entry(flag_file,
                                      {'mode': 'manual', 'antenna': antenna_id, 'reason': BAD_ANTENNA_TIME,
                                       'correlation': polarization,
                                       'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def flag_bad_baseline_time(self, flag_file, polarization, scan_id, baseline, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        self.flag_recorder.mark_entry(flag_file,
                                      {'mode': 'manual', 'antenna': str(baseline), 'reason': BAD_BASELINE_TIME,
                                       'correlation': polarization,
                                       'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def get_bad_antennas_with_scans_for(self, polarization, source_id):
        scan_ids = self.scan_ids(source_id, polarization)
        bad_antennas_with_scans = {}
        for scan_id in scan_ids:
            bad_antennas = self.flagged_antennas[polarization][scan_id]
            for antenna in bad_antennas:
                if not antenna in bad_antennas_with_scans: bad_antennas_with_scans[antenna] = []
                bad_antennas_with_scans[antenna].append(scan_id)
        return bad_antennas_with_scans

    def split(self, output_ms, filters):
        self.casa_runner.split(output_ms, filters)

    def generate_flag_summary(self, reason):
        self.casa_runner.generate_flag_summary(reason, self.scan_ids())
