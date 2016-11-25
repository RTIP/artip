import casac
import itertools
from phase_set import PhaseSet


class MeasurementSet:
    def __init__(self, dataset):
        self.__ms = casac.casac.ms()
        self.__ms.open(dataset)
        self.__metadata = self.__ms.metadata()

    def __del__(self):
        self.__ms.close()

    def _filter(self, filters={}):
        extra_filters = filters['extra_filters']
        primary_filters = filters['primary_filters']
        self.__ms.selectinit(reset=True)
        for filter_name, value in primary_filters.iteritems():
            getattr(self.__ms, "select" + filter_name)(value)
        if extra_filters: self.__ms.select(extra_filters)

    def _get_data(self,filter_params, selection_params):
        self._filter(filter_params)
        data_items = self.__ms.getdata(selection_params)
        return data_items

    def get_phase_data(self,filter_params):
        return PhaseSet(self._get_data(filter_params, ['phase'])['phase'][0][0])

    def scan_ids_for(self, source_id):
        scan_ids = self.__metadata.scansforfield(source_id)
        return map(lambda scan_id: int(scan_id), scan_ids)

    def baselines(self):
        antennaids = self.__metadata.antennaids()  # Throws error as number of antennas is 30 and this shows more.
        antennaids = range(0, 29, 1)  # Fix : Hard coded, should be removed
        baselines = list(itertools.combinations(antennaids, 2))
        return map(lambda baseline: (int(baseline[0]), int(baseline[1])), baselines)
