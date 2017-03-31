from configs import config
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
    return ms.statistics(column="CORRECTED_DATA", complex_value='amp', field=",".join(map(str,fields)))['CORRECTED']


def is_subset(superset, subset):
    return set(subset.items()).issubset(set(superset.items()))
