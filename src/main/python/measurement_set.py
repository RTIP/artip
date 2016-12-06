import itertools

import casac

from models.phase_set import PhaseSet
from models.antenna import Antenna


class MeasurementSet:
    def __init__(self, dataset):
        self.__ms = casac.casac.ms()
        self.__ms.open(dataset)
        self.__metadata = self.__ms.metadata()

    def __del__(self):
        self.__ms.close()

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
        scan_ids = self.__metadata.scansforfield(source_id)
        return map(lambda scan_id: int(scan_id), scan_ids)


    def baselines(self):
        baselines = list(itertools.combinations(self.antennaids(), 2))
        return map(lambda baseline: (int(baseline[0]), int(baseline[1])), baselines)


    def antennaids(self):
        # return self.__metadata.antennaids()  # Throws error as number of antennas is 30 and this shows more.
        return range(0, 29, 1)  # Fix : Hard coded, should be removed and also enable unit tests for the same


    def antennas(self):
        antenna_list = []
        for antenna_id in self.antennaids():
            antenna_list.append(Antenna(antenna_id))
        return antenna_list
