import sys

growtime = float(sys.argv[-1])
growfreq = float(sys.argv[-2])
timedevscale = float(sys.argv[-3])
freqdevscale = float(sys.argv[-4])
channels_to_average = sys.argv[-8]
spw = "{0}:{1}".format(sys.argv[-5], channels_to_average)
field = sys.argv[-6]
ms_dataset = sys.argv[-7]
maxnpieces = sys.argv[-13]
usewindowstats = sys.argv[-12]
halfwin = int(sys.argv[-11])
freqcutoff = float(sys.argv[-10])
timecutoff = float(sys.argv[-9])

tfcrop_command = "mode='tfcrop' maxnpieces={0} usewindowstats='{1}' halfwin={2} timecutoff={3}" \
                 " freqcutoff={4}".format(maxnpieces, usewindowstats, halfwin, timecutoff, freqcutoff)

r_flag_command = "mode='rflag' extendflags=False timedevscale={0} freqdevscale={1} ".format(timedevscale, freqdevscale)

extend_flag_command = "mode='extend' growaround=True flagnearfreq=True flagneartime=True" \
                      " extendpols=False growtime={0} growfreq={1}".format(growtime, growfreq)

cmdlist = [tfcrop_command, r_flag_command, extend_flag_command]

flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, display='data', field=field, datacolumn='corrected', spw=spw)
