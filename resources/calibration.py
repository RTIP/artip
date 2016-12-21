

gaincal(vis='may14.ms', caltable='fluxcal.table', field='0', refant='2', calmode='ap', solint='2', minsnr=2.0, spw='0:100')
applycal(vis='may14.ms', field='0', gaintable=['fluxcal.table'], gainfield=['0'], calwt=F)
gaincal(vis='may14.ms', caltable='bpphase.gcal', field='0', refant='2', calmode='p', solint='2', minsnr=2.0, spw='0:80~120')
bandpass(vis='may14.ms',caltable='bandpass.table',field='0', refant='2', solint='inf', solnorm=T, gaintable=['bpphase.gcal'])
applycal(vis='may14.ms', field='0', gaintable=['bandpass.table','fluxcal.table'], gainfield=['0','0'], calwt=F)



gaincal(vis='aug7.ms', caltable='aug_fluxcal.table', field='0', refant='2', calmode='ap', solint='2', minsnr=2.0, spw='0:100')
applycal(vis='aug7.ms', field='0', gaintable=['aug_fluxcal.table'], gainfield=['0'], calwt=F)
