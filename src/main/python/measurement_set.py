import itertools
import logging
import casac
import numpy
from datetime import datetime, timedelta
from configs.config import GLOBAL_CONFIG
from helpers import minus
from models.phase_set import PhaseSet
from models.antenna import Antenna
from models.antenna_state import AntennaState
from casa.flag_recorder import FlagRecorder
from casa.flag_reasons import BAD_ANTENNA, BAD_ANTENNA_TIME, BAD_BASELINE_TIME
from terminal_color import Color
from casa.casa_runner import CasaRunner


class MeasurementSet:
    def __init__(self, dataset):
        self.__ms = casac.casac.ms()
        self.__ms.open(dataset)
        self.__metadata = self.__ms.metadata()
        self.antennas = self.create_antennas()
        self.flag_data = self._initialize_flag_data()

    def __del__(self):
        self.__ms.close()

    def _initialize_flag_data(self):
        flag_data = {
            polarization: {scan_id: {'antennas': [], 'baselines': []} for scan_id in self._scan_ids()} for
            polarization in
            GLOBAL_CONFIG['polarizations']}
        return flag_data

    def _filter(self, channel, polarization, filters={}):
        self.__ms.selectinit(reset=True)
        self.__ms.selectpolarization(polarization)
        self.__ms.selectchannel(**channel)
        if filters: self.__ms.select(filters)

    def get_data(self, channel, polarization, filters, selection_params, ifraxis=False):
        self._filter(channel, polarization, filters)
        data_items = self.__ms.getdata(selection_params, ifraxis=ifraxis)
        return data_items

    def get_phase_data(self, channel, polarization, filters={}):
        return PhaseSet(self.get_data(channel, polarization, filters, ['phase'])['phase'][0][0])

    def get_field_name_for(self, field_id):
        return self.__metadata.fieldnames()[field_id]

    def scan_ids_for(self, source_id):
        try:
            scan_ids = self.__metadata.scansforfield(source_id)
            return map(lambda scan_id: int(scan_id), scan_ids)
        except RuntimeError:
            return []

    def baselines(self):
        baselines = list(itertools.combinations(self.antennaids(), 2))
        return map(lambda baseline: (int(baseline[0]), int(baseline[1])), baselines)

    def baselines_for(self, antenna):
        remaining_antennas = list(self.antennas)
        remaining_antennas.remove(antenna)
        baselines = list(itertools.product(remaining_antennas, [antenna]))

        def sort_antennas(baseline):
            sorted_baseline = tuple(sorted(list(baseline), key=lambda antenna: antenna.id))
            return sorted_baseline

        return map(sort_antennas, baselines)

    def create_antennas(self):
        antennas = map(lambda id: Antenna(id), self.antennaids())
        scan_ids = self._scan_ids()
        product_pol_scan_ant = itertools.product(GLOBAL_CONFIG['polarizations'], scan_ids, antennas)

        for polarization, scan_id, antenna in product_pol_scan_ant:
            antennaState = AntennaState(antenna.id, polarization, scan_id)
            antenna.add_state(antennaState)

        return antennas

    def antennaids(self):
        # return self.__metadata.antennaids()  # Throws error as number of antennas is 30 and this shows more.
        return range(0, 29, 1)  # Fix : Hard coded, should be removed and also enable unit tests for the same

    def unflagged_antennaids(self, polarization, scan_id):
        return minus(self.antennaids(), self.flag_data[polarization][scan_id]['antennas'])

    def antenna_count(self):
        return len(self.antennas)

    def _scan_ids(self):
        return self.__metadata.scannumbers()

    def timesforscan(self, scan_id):
        quanta = casac.casac.quanta()
        times_with_second = map(lambda time: str(time) + 's', self.__metadata.timesforscan(scan_id))
        return numpy.array(
            map(lambda time: quanta.time(quanta.quantity(time), form='ymd'), times_with_second)).flatten()

    def flag_antennas(self, polarization, scan_id, antenna_ids):
        if antenna_ids:
            FlagRecorder.mark_entry(
                {'mode': 'manual', 'antenna': ','.join(map(lambda antenna_id: str(antenna_id), antenna_ids)),
                 'reason': BAD_ANTENNA, 'correlation': polarization,
                 'scan': scan_id})
            self.flag_data[polarization][scan_id]['antennas'] += antenna_ids

    def flag_baselines(self, polarization, scan_id, baselines):
        self.flag_data[polarization][scan_id]['baselines'] += baselines

    def flag_bad_antennas(self, is_bad):
        for antenna in self.antennas:
            for state in antenna.get_states():
                if state.scan_id in self._scan_ids() and is_bad(state):
                    self.flag_antennas(state.polarization, state.scan_id, [antenna.id])

        CasaRunner.flagdata(BAD_ANTENNA)
        logging.info(Color.HEADER + 'Flagged above antennas in CASA' + Color.ENDC)

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
        FlagRecorder.mark_entry(
            {'mode': 'manual', 'antenna': antenna_id, 'reason': BAD_ANTENNA_TIME, 'correlation': polarization,
             'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})

    def flag_bad_baseline_time(self, polarization, scan_id, baseline, timerange):
        timerange_for_flagging = self._get_timerange_for_flagging(timerange)
        FlagRecorder.mark_entry(
            {'mode': 'manual', 'antenna': str(baseline), 'reason': BAD_BASELINE_TIME, 'correlation': polarization,
             'scan': scan_id, 'timerange': '~'.join(timerange_for_flagging)})
