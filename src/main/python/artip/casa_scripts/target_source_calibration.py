import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

ms_dataset = parameters[0]
output_path = parameters[1]
flux_cal_field = parameters[2]
phase_cal_field = parameters[3]
target_source_field = parameters[4]

bandpass_table = output_path + "/" + 'bandpass.bcal'
scanphase_gcal = output_path + "/" + 'scanphase.gcal'
flux_gcal = output_path + "/" + 'flux.gcal'

applycal(vis=ms_dataset, field=target_source_field, gaintable=[bandpass_table, scanphase_gcal, flux_gcal],
         gainfield=[flux_cal_field, phase_cal_field, phase_cal_field], calwt=F, applymode='calonly')