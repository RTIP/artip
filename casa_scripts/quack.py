import sys
import distutils.util

ms_dataset = sys.argv[-2]
show_percent = bool(distutils.util.strtobool(sys.argv[-1]))
flagdata(vis=ms_dataset, mode='quack', quackinterval=48, quackmode='beg')
