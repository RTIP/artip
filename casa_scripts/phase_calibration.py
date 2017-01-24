import sys

ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
flux_cal_field = sys.argv[-3]
phase_cal_field = sys.argv[-2]
channels_to_average = sys.argv[-1]
spw = "0:{0}".format(channels_to_average)

fields = "{0},{1}".format(flux_cal_field, phase_cal_field)
refant = '2'

flux_table = output_path + "/" + 'fluxcal.table'
phase_table = output_path + "/" + 'phasecal.table'
scaled_phase_table = output_path + "/" + 'scaled_phase.table'
bandpass_table = output_path + "/" + 'bandpass.table'

gaincal(vis=ms_dataset, caltable=phase_table, field=fields, refant=refant, calmode='ap', solint='2', minsnr=2.0,
        spw=spw, gaintable=[flux_table, bandpass_table])

fluxscale(vis=ms_dataset, caltable=phase_table, fluxtable=scaled_phase_table, reference=flux_cal_field)
applycal(vis=ms_dataset, field=phase_cal_field, gaintable=[scaled_phase_table], gainfield=[phase_cal_field], calwt=F)
