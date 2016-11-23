from angular_dispersion import is_dispersed
from config import Config
from measurement_set import MeasurementSet

def main(ms_dataset):
    ms = MeasurementSet(ms_dataset)
    config=Config('./conf/config.yml')

    global_properties = config.global_configs()
    flux_cal_properties = config.flux_cal_configs()
    baselines = ms.baselines()
    scans = ms.scan_ids_for(flux_cal_properties['field'])

    bad_baselines = {}
    print "Calculating bad baselines for angular dispersion in phases lesser than", flux_cal_properties['r_threshold'],"......"
    for polarization in global_properties['polarizations']:
        for scan in scans:
            for baseline in baselines:
                ms.filter({'polarization': polarization, 'channel': flux_cal_properties['channel']},
                          {'scan_number': scan, 'antenna1': baseline[0], 'antenna2': baseline[1]})
                phase_data = ms.get_data(['phase'])['phase'][0][0]

                if is_dispersed(phase_data, flux_cal_properties['r_threshold']):
                    if not polarization in bad_baselines.keys():
                        bad_baselines[polarization] = {}
                    if not scan in bad_baselines[polarization].keys():
                        bad_baselines[polarization][scan] = []
                    bad_baselines[polarization][scan].append(baseline)
    print bad_baselines

if __name__ == "__main__":
    main()
