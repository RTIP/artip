import casac
import itertools
from angular_dispersion import is_dispersed
from ConfigParser import ConfigParser
import ast
import math


def main(ms_dataset):
    config = ConfigParser()
    config.read('./conf/config.cfg')

    field = config.getint('Flux Calibration', 'field')
    channel = config.getint('Flux Calibration', 'channel')
    r_threshold = config.getfloat('Flux Calibration', 'r_threshold')
    polarizations = ast.literal_eval(config.get('Global', 'polarizations'))
    ms = casac.casac.ms()
    ms.open(ms_dataset)

    metadata = ms.metadata()
    antenna_ids = metadata.antennaids()  # Throws error as number of antennas is 30 and this shows more.
    antenna_ids = range(0, 29, 1)
    baselines = list(itertools.combinations(antenna_ids, 2))
    scans = metadata.scansforfield(field)

    bad_baselines = {}
    print "Calculating bad baselines for angular dispersion in phases lesser than", r_threshold,"......"
    for polarization in polarizations:
        for scan in scans:
            for baseline in baselines:
                ms.selectinit(reset=True)
                ms.selectpolarization(polarization)
                ms.selectchannel(channel)
                ms.select({'scan_number': int(scan), 'antenna1': int(baseline[0]), 'antenna2': int(baseline[1])})
                phase_data = ms.getdata(['phase'])['phase'][0][0]

                if is_dispersed(phase_data, r_threshold):
                    if not polarization in bad_baselines.keys():
                        bad_baselines[polarization] = {}
                    if not scan in bad_baselines[polarization].keys():
                        bad_baselines[polarization][scan] = []
                    bad_baselines[polarization][scan].append(baseline)
    print bad_baselines


if __name__ == "__main__":
    main()
