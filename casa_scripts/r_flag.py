import sys

growtime = float(sys.argv[-1])
growfreq = float(sys.argv[-2])
timedevscale = float(sys.argv[-3])
freqdevscale = float(sys.argv[-4])
spw = sys.argv[-5]
field = sys.argv[-6]
ms_dataset = sys.argv[-7]

flagdata(vis=ms_dataset, mode='rflag', field=field, spw=spw, datacolumn='corrected',
         freqdevscale=freqdevscale, timedevscale=timedevscale,
         growtime=growtime, growfreq=growfreq)

# freqdevscale  => deviations from the calculated RMS in frequency (the default is 5.0).
# timedevscale  => deviations from the calculated RMS in time (the default is 5.0).
# growtime=50.0 => will flag all data for a given channel if more than 50% of that channel's
#                  time is already flagged.
# growfreq=90.0 => will flag the entire spectrum for an integration if more than 90% of the
#                  channels in that integration are already flagged.
