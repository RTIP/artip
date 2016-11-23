import casac
import itertools

class MeasurementSet:
    def __init__(self,dataset):
         self.__ms = casac.casac.ms()
         self.__ms.open(dataset)
         self.__metadata = self.__ms.metadata()

    def filter(self,primary_filters={}, extra_filters = {}):
        self.__ms.selectinit(reset=True)
        for filter_name, value in primary_filters.iteritems():
            getattr(self.__ms, "select"+filter_name)(value)
        if extra_filters: self.__ms.select(extra_filters)


    def get_data(self, params):
        return self.__ms.getdata(params)

    def scan_ids_for(self, source_id):
        scan_ids = self.__metadata.scansforfield(source_id)
        return map(lambda scan_id: int(scan_id), scan_ids)

    def baselines(self):
        antennaids = self.__metadata.antennaids() # Throws error as number of antennas is 30 and this shows more.
        antennaids = range(0,29,1) # Fix : Hard coded, should be removed
        baselines = list(itertools.combinations(antennaids, 2))
        return map(lambda baseline: (int(baseline[0]), int(baseline[1])), baselines)
