import sys

ms_dataset = sys.argv[-1]

gaincal(vis=ms_dataset, caltable='phasecal.table', field='0,1', refant='2', calmode='ap', solint='2', minsnr=2.0,
        spw='0:100', gaintable=['fluxcal.table', 'bandpass.table'])

fluxscale(vis=ms_dataset, caltable='phasecal.table', fluxtable='scaled_phase.table', reference='0')
applycal(vis=ms_dataset, field='1', gaintable=['scaled_phase.table'], gainfield=['1'], calwt=F)
