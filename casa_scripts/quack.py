import sys
import distutils.util

ms_dataset = sys.argv[-2]
show_percent = bool(distutils.util.strtobool(sys.argv[-1]))
flagdata(vis=ms_dataset, mode='quack', quackinterval=48, quackmode='beg')

if show_percent:
    summary = flagdata(vis=ms_dataset, mode='summary')
    percent_flagged = summary['flagged'] / summary['total'] * 100
    print ">>> Total data flagged {0}".format(percent_flagged)
