import sys

ms_dataset = sys.argv[-6]
output_path = sys.argv[-5]
field = sys.argv[-4]
refant = sys.argv[-3]
minsnr = float(sys.argv[-2])
spw = sys.argv[-1]

bpphase_table = output_path + "/" + 'bpphase.gcal'
bandpass_table = output_path + "/" + 'bandpass.table'
fluxcal_table = output_path + "/" + 'fluxcal.table'

gaincal(vis=ms_dataset, caltable=bpphase_table, field='0', refant='2', calmode='p', solint='2', minsnr=minsnr,
        spw=spw)
bandpass(vis=ms_dataset, caltable=bandpass_table, field='0', refant='2', solint='inf', solnorm=T,
         gaintable=[bpphase_table])
applycal(vis=ms_dataset, field='0', gaintable=[bandpass_table, fluxcal_table], gainfield=['0', '0'], calwt=F)
