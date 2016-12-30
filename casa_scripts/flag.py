import sys
import os

ms_dataset = sys.argv[-2]
reason = sys.argv[-1]
flag_file = os.path.realpath('casa_scripts/flags.txt')
flagdata(vis=ms_dataset, inpfile=flag_file, reason=reason, mode='list')