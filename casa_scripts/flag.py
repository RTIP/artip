import sys
import os

ms_dataset = sys.argv[-3]
flag_file = sys.argv[-2]
reason = sys.argv[-1].split(",")
flag_file_full_path = os.path.realpath(flag_file)
flagdata(vis=ms_dataset, inpfile=flag_file_full_path, reason=reason, mode='list')

summary = flagdata(vis=ms_dataset, mode='summary')
percent_flagged = summary['flagged'] / summary['total'] * 100

print ">>> Total data flagged {0} %".format(percent_flagged)

