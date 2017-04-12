import sys

channels_to_average = sys.argv[-11]
spw = sys.argv[-3]
spw_with_freq = "{0}:{1}".format(spw, channels_to_average)
field = sys.argv[-4]
ms_dataset = sys.argv[-5]
datacolumn = sys.argv[-12]
maxnpieces = sys.argv[-10]
usewindowstats = sys.argv[-9]
halfwin = int(sys.argv[-8])
freqcutoff = float(sys.argv[-7])
timecutoff = float(sys.argv[-6])

growtime = float(sys.argv[-1])
growfreq = float(sys.argv[-2])

tfcrop_command = "mode='tfcrop' extendflags=False maxnpieces={0} usewindowstats='{1}' halfwin={2} timecutoff={3}" \
                 " freqcutoff={4}  spw='{5}' datacolumn={6} field='{7}'".format(maxnpieces, usewindowstats, halfwin,
                                                                              timecutoff,
                                                                              freqcutoff,
                                                                              spw_with_freq, datacolumn, field)

extend_flag_command = "mode='extend' growaround=False flagnearfreq=False flagneartime=False" \
                      " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                      "field='{4}'".format(growtime, growfreq, spw, datacolumn, field)

cmdlist = [tfcrop_command, extend_flag_command]

flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply')
