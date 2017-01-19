import sys
import os

ms_dataset = sys.argv[-3]
flag_file = sys.argv[-2]
reason = sys.argv[-1]
flag_file_full_path = os.path.realpath(flag_file)
flagdata(vis=ms_dataset, inpfile=flag_file_full_path, reason=reason, mode='list')