import os
import sys
import yaml
import subprocess
import time


def load_config(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs


config = load_config(sys.argv[1])
dataset = config['dataset']
nChunks = config['nChunks']
parallel = config['parallel']
nCores = config['nCores']
hostfile = config['hostfile']
casapy_path = config['casapy_path']
output_path = "{0}/{1}".format(config['output_path'], os.path.splitext(os.path.basename(dataset))[0])
ms_chunks_path = "{0}/ms_chunks".format(output_path)
image_path = "{0}/images".format(output_path)
logs_path = "{0}/logs".format(output_path)
total_channels = config['total_channels']
spw = config['spw']
nchan = total_channels / nChunks
processes = []


def run(script_path, script_parameters, output_dataset):
    log_file = "{0}/casa-{1}.log".format(logs_path, os.path.splitext(os.path.basename(output_dataset))[0])

    if parallel:
        command = "mpicasa --hostfile {0} --mca btl_tcp_if_include em1 --mca oob_tcp_if_include em1 -n {1} {2} --nologger --nogui  --logfile {3} -c {4} {5}".format(
            hostfile, nCores, casapy_path, log_file, script_path, script_parameters)
    else:
        command = "{0} --nologger --logfile {1} -c {2} {3}".format(casapy_path,
                                                                   log_file, script_path,
                                                                   script_parameters)

    print "Executing command -> ", command
    return subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file("outputfile", 'a+'), shell=True)


def split(min_chan, max_chan):
    while max_chan < total_channels:
        spw_with_chan = "{0}:{1}~{2}".format(spw, min_chan, max_chan)
        script_path = 'split_dataset.py'
        output_dataset = ms_chunks_path + "/{0}_{1}.ms".format(min_chan, max_chan)
        script_parameters = "{0} {1} {2} {3}".format(dataset, spw_with_chan, output_dataset, "data")
        p = run(script_path, script_parameters, output_dataset)
        time.sleep(0.5)
        processes.append(p)
        min_chan = max_chan + 1
        max_chan = max_chan + nchan


def tclean():
    for filename in os.listdir(ms_chunks_path):
        if filename.endswith('.ms'):
            script_path = 'tclean.py'
            output_dataset = ms_chunks_path + "/{0}".format(filename)
            image_name = image_path + "/{0}".format(filename)
            script_parameters = "{0} {1} {2}".format(output_dataset, parallel, image_name)
            run(script_path, script_parameters, output_dataset)
            time.sleep(1.0)


def wait_for_process_execution():
    print "Processes are ", processes
    for p in processes:
        p.wait()
    print "Done with set of process"


def create_output_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    split(0, nchan - 1)
    wait_for_process_execution()
    tclean()
    wait_for_process_execution()


def setup():
    create_output_dir(output_path)
    create_output_dir(ms_chunks_path)
    create_output_dir(logs_path)
    create_output_dir(image_path)


if __name__ == "__main__":
    setup()
    main()
