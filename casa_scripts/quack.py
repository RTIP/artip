import sys

ms_dataset = sys.argv[-1]
flagdata(vis=ms_dataset, mode='quack', quackinterval=48, quackmode='beg')

summary = flagdata(vis=ms_dataset, mode='summary')
percent_flagged = summary['flagged'] / summary['total'] * 100

print ">>> Total data flagged {0} %".format(percent_flagged)
