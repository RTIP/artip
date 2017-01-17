import sys

ms_dataset = sys.argv[-5]
field = sys.argv[-4]
refant = sys.argv[-3]
minsnr = float(sys.argv[-2])
spw = sys.argv[-1]
gaincal(vis=ms_dataset, caltable='bpphase.gcal', field='0', refant='2', calmode='p', solint='2', minsnr=minsnr,
        spw=spw)
bandpass(vis=ms_dataset, caltable='bandpass.table', field='0', refant='2', solint='inf', solnorm=T,
         gaintable=['bpphase.gcal'])
applycal(vis=ms_dataset, field='0', gaintable=['bandpass.table', 'fluxcal.table'], gainfield=['0', '0'], calwt=F)
