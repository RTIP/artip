import sys
import os
import distutils.util

ms_dataset = sys.argv[-4]
flag_file = sys.argv[-3]
reason = sys.argv[-2].split(",")
show_percent = bool(distutils.util.strtobool(sys.argv[-1]))
flag_file_full_path = os.path.realpath(flag_file)
flagdata(vis=ms_dataset, inpfile=flag_file_full_path, reason=reason, mode='list')

if show_percent:
    summary = flagdata(vis=ms_dataset, mode='summary')
    percent_flagged = summary['flagged'] / summary['total'] * 100
    print ">>> Total data flagged {0} %".format(percent_flagged)
