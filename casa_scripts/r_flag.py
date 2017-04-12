import sys

datacolumn = sys.argv[-9]
growtime = float(sys.argv[-1])
growfreq = float(sys.argv[-2])
timedevscale = float(sys.argv[-3])
freqdevscale = float(sys.argv[-4])
channels_to_average = sys.argv[-8]
spw = sys.argv[-5]
spw_with_freq = "{0}:{1}".format(spw, channels_to_average)
field = sys.argv[-6]
ms_dataset = sys.argv[-7]

r_flag_command = "mode='rflag' extendflags=False timedevscale={0} " \
                 "freqdevscale={1}  spw='{2}' datacolumn='{3}' field='{4}' ".format(timedevscale, freqdevscale,
                                                                                  spw_with_freq,
                                                                                  datacolumn, field)

extend_flag_command = "mode='extend' growaround=True flagnearfreq=True flagneartime=True" \
                      " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                      "field='{4}'".format(growtime, growfreq, spw, datacolumn, field)

cmdlist = [r_flag_command, extend_flag_command]

flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply', display='data')
