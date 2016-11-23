import casac
import itertools
from angular_dispersion import is_dispersed
from config import Config

def main(ms_dataset):
    ms = casac.casac.ms()
    ms.open(ms_dataset)
    metadata = ms.metadata()

    config=Config('./conf/config.yml')

    global_properties = config.global_configs()
    flux_cal_properties = config.flux_cal_configs()

    antenna_ids = metadata.antennaids()  # Throws error as number of antennas is 30 and this shows more.
    antenna_ids = range(0, 29, 1)
    baselines = list(itertools.combinations(antenna_ids, 2))
    scans = metadata.scansforfield(flux_cal_properties['field'])

    bad_baselines = {}
    print "Calculating bad baselines for angular dispersion in phases lesser than", flux_cal_properties['r_threshold'],"......"
    for polarization in global_properties['polarizations']:
        for scan in scans:
            for baseline in baselines:
                ms.selectinit(reset=True)
                ms.selectpolarization(polarization)
                ms.selectchannel(flux_cal_properties['channel'])
                ms.select({'scan_number': int(scan), 'antenna1': int(baseline[0]), 'antenna2': int(baseline[1])})
                phase_data = ms.getdata(['phase'])['phase'][0][0]

                if is_dispersed(phase_data, flux_cal_properties['r_threshold']):
                    if not polarization in bad_baselines.keys():
                        bad_baselines[polarization] = {}
                    if not scan in bad_baselines[polarization].keys():
                        bad_baselines[polarization][scan] = []
                    bad_baselines[polarization][scan].append(baseline)
    print bad_baselines

if __name__ == "__main__":
    main()
