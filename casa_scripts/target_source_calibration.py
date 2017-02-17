import sys

ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
flux_cal_field = sys.argv[-3]
phase_cal_field = sys.argv[-2]
target_source_field = sys.argv[-1]

bandpass_table = output_path + "/" + 'bandpass.bcal'
scanphase_gcal = output_path + "/" + 'scanphase.gcal'
flux_gcal = output_path + "/" + 'flux.gcal'

applycal(vis=ms_dataset, field=target_source_field, gaintable=[bandpass_table, scanphase_gcal, flux_gcal],
         gainfield=[flux_cal_field, phase_cal_field, phase_cal_field], calwt=F, applymode='calonly')