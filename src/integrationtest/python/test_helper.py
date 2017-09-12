from configs import config
from configs.config_loader import ConfigLoader
import casac
import subprocess, time


def fits_to_ms(fits_file, ms_path):
    logfile = config.OUTPUT_PATH + "/casa.log"
    casapy_path = config.CASAPY_CONFIG['path']
    import_task = "importgmrt(fitsfile='{0}',vis='{1}')".format(fits_file, ms_path)
    command = "{0} --nologger --nogui  --logfile {1} -c \"{2}\"".format(casapy_path, logfile, import_task)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    while process.poll() is None:
        time.sleep(1)


def get_stats(ms_path, fields):
    ms = casac.casac.ms()
    ms.open(ms_path)
    return ms.statistics(column="CORRECTED_DATA", complex_value='amp', field=",".join(map(str, fields)))['CORRECTED']


def is_subset(superset, subset):
    return set(subset.items()).issubset(set(superset.items()))


def expected_stats(_for, seed_data_path, dataset_name):
    expected_stats_path = "{0}/{1}/expected_stats.yml".format(seed_data_path, dataset_name)
    expected_stats = ConfigLoader().load(expected_stats_path)[_for]
    return expected_stats


def _load_image():
    ap_loop_count = 1

    image = casac.casac.image()
    image_path = "{0}/self_caled_ap/self_cal_image_ap_{1}.image".format(config.OUTPUT_PATH, ap_loop_count)
    image.open(image_path)
    return image


def _get_image_stats(region):
    image = _load_image()
    return image.statistics(region=region)


def image_rms(rms_region):
    coordinate1, coordinate2 = rms_region['cordinate1'], rms_region['cordinate2']
    region = "box [ [ {0}pix , {1}pix] , [{2}pix, {3}pix ] ]".format(coordinate1[0], coordinate1[1],
                                                                     coordinate2[0], coordinate2[1])
    return _get_image_stats(region)['rms']


def image_flux(flux_region):
    center, radius = flux_region['centre'], flux_region['radius']
    region = "circle [ [ {0}pix , {1}pix] ,{2}pix ]".format(center[0], center[1], radius)
    return _get_image_stats(region)['flux'][0]


def image_beam():
    image = _load_image()
    restoringbeam = image.restoringbeam()
    return restoringbeam['major']['value'], restoringbeam['minor']['value']


def enable_flagging_and_calibration():
    config.STAGE_CONFIGS.update({'flux_calibration': True, 'bandpass_calibration': True,
                                          'phase_calibration': True})


def disable_flagging_and_calibration():
    config.STAGE_CONFIGS.update({'flux_calibration': False, 'bandpass_calibration': False,
                                          'phase_calibration': False})


def enable_imaging():
    config.STAGE_CONFIGS.update({'target_source': {
        'run_auto_flagging': True,
        'create_continuum': True,
        'create_line_image': True
    }})


def disable_imaging():
    config.STAGE_CONFIGS.update({'target_source': {
        'run_auto_flagging': False,
        'create_continuum': False,
        'create_line_image': False
    }})
