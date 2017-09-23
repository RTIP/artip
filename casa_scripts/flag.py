import sys
import os
import distutils.util

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

ms_dataset = parameters[0]
flag_file = parameters[1]
reason = parameters[2].split(",")
show_percent = bool(distutils.util.strtobool(parameters[3]))

if len(reason) == 1:  reason = reason[0]
flag_file_full_path = os.path.realpath(flag_file)
flagdata(vis=ms_dataset, inpfile=flag_file_full_path, reason=reason, mode='list')

if show_percent:
    summary = flagdata(vis=ms_dataset, mode='summary')
    percent_flagged = summary['flagged'] / summary['total'] * 100
    print ">>> Total data flagged {0} %".format(percent_flagged)
