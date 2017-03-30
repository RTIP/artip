from configs import config
import os
import subprocess,time

def fits_to_ms(fits_file, ms_path):
    logfile = config.OUTPUT_PATH + "/casa.log"
    casapy_path = config.CASAPY_CONFIG['path']
    import_task = "importgmrt(fitsfile='{0}',vis='{1}')".format(fits_file, ms_path)
    command = "{0} --nologger --nogui  --logfile {1} -c \"{2}\"".format(casapy_path, logfile, import_task)
    # os.system(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    while process.poll() is None:
        time.sleep(1)
