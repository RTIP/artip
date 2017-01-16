import sys

ms_dataset = sys.argv[-4]
flux_cal_field = sys.argv[-3]
phase_cal_field = sys.argv[-2]
channels_to_average = sys.argv[-1]
spw = "0:{0}".format(channels_to_average)

fields = "{0},{1}".format(flux_cal_field, phase_cal_field)
refant = '2'

gaincal(vis=ms_dataset, caltable='phasecal.table', field=fields, refant=refant, calmode='ap', solint='2', minsnr=2.0,
        spw=spw, gaintable=['fluxcal.table', 'bandpass.table'])

fluxscale(vis=ms_dataset, caltable='phasecal.table', fluxtable='scaled_phase.table', reference=flux_cal_field)
applycal(vis=ms_dataset, field=phase_cal_field, gaintable=['scaled_phase.table'], gainfield=[phase_cal_field], calwt=F)
