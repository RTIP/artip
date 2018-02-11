import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

ms_dataset = parameters[0]
output_path = parameters[1]
field = parameters[2]
refant = parameters[3]
solint = float(parameters[4])
phase_calib_minsnr = float(parameters[5])
phase_calib_solint = float(parameters[6])

bpphase_gcal = output_path + "/" + 'bpphase.gcal'
bandpass_table = output_path + "/" + 'bandpass.bcal'

sys.stdout.write("\n##### Started calculating bandpass gains on {0}#####\n".format(ms_dataset))
gaincal(vis=ms_dataset, caltable=bpphase_gcal, field=field, refant=refant, calmode='p', solint=phase_calib_solint, minsnr=phase_calib_minsnr)
sys.stdout.write("\n##### Finished calculating bandpass gains on {0}#####\n".format(ms_dataset))

bandpass(vis=ms_dataset, caltable=bandpass_table, field=field, refant=refant, solint=solint, solnorm=T,
         gaintable=[bpphase_gcal], combine='field')
