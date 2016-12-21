import itertools

import casac
from config import *
from helpers import *
from models.phase_set import PhaseSet
from models.antenna import Antenna
from models.antenna_state import AntennaState
from models.antenna_status import AntennaStatus


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
        flag_data = {polarization: {scan_id: {'antennas': []} for scan_id in self._scan_ids()} for polarization in
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

    def unflagged_antennaids(self,polarization, scan_id):
        return minus(self.antennaids(),self.flag_data[polarization][scan_id]['antennas'])

    def antenna_count(self):
        return len(self.antennas)

    def _scan_ids(self):
        return self.__metadata.scannumbers()

    def flag_antenna(self, polarization, scan_id, antenna_ids):
        self.flag_data[polarization][scan_id]['antennas'] += antenna_ids

    def flag_r_and_closure_based_bad_antennas(self):
        for antenna in self.antennas:
            for state in antenna.get_states():
                if state.scan_id in self._scan_ids() and (
                                state.get_R_phase_status() == AntennaStatus.BAD and state.get_closure_phase_status() == AntennaStatus.BAD):
                    self.flag_antenna(state.polarization, state.scan_id, [antenna.id])
        # print "*********** flagged antenna with R and Closure",self.flag_data
        # self.flag_antenna('RR', 1, [1,7,11])