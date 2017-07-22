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
output_path = config['output_path']
image_path = config['image_path']
total_channels = config['total_channels']
spw = config['spw']
nchan = total_channels / nChunks
processes = []


def run(script_path, script_parameters):
    if parallel:
        command = "mpicasa --hostfile {0} --mca btl_tcp_if_include em1 --mca oob_tcp_if_include em1 -n {1} {2} --nologger --nogui  --logfile {3} -c {4} {5}".format(
            hostfile, nCores, casapy_path, "mpicasa.log", script_path, script_parameters)
    else:
        command = "{0} --nologger --logfile {1} -c {2} {3}".format(casapy_path, "casa.log", script_path,
                                                                   script_parameters)

    print "Executing command -> ", command
    return subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file("outputfile", 'a+'), shell=True)


def split(min_chan, max_chan):
    if max_chan > total_channels:
        return
    spw_with_chan = "{0}:{1}~{2}".format(spw, min_chan, max_chan)
    print spw_with_chan
    script_path = 'split_dataset.py'
    output_dataset = output_path + "/{0}_{1}.ms".format(min_chan, max_chan)
    script_parameters = "{0} {1} {2} {3}".format(spw_with_chan, dataset, output_dataset, "data")
    p = run(script_path, script_parameters)
    time.sleep(0.50)
    processes.append(p)
    split(max_chan + 1, max_chan + nchan)


def tclean():
    for filename in os.listdir(output_path):
        if not filename.startswith('.'):
            script_path = 'tclean.py'
            output_dataset = output_path + "/{0}".format(filename)
            image_name = image_path + "/{0}".format(filename)
            script_parameters = "{0} {1} {2}".format(output_dataset, parallel, image_name)
            run(script_path, script_parameters)


def wait_for_process_execution():
    print "Processes are ", processes
    for p in processes:
        p.wait()
    print "Done with set of process"


def main():
    split(0, nchan - 1)
    wait_for_process_execution()
    tclean()
    wait_for_process_execution()


if __name__ == "__main__":
    main()
