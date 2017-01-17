import sys

ms_dataset = sys.argv[-2]
field = sys.argv[-1]


applycal(vis=ms_dataset, field=field, gaintable=['bandpass.table','scaled_phase.table'], gainfield=['0','1'], calwt=F)
