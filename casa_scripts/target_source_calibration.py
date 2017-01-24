import sys

ms_dataset = sys.argv[-3]
output_path = sys.argv[-2]
field = sys.argv[-1]

bandpass_table = output_path + "/" + 'bandpass.table'
scaled_phase_table = output_path + "/" + 'scaled_phase.table'

applycal(vis=ms_dataset, field=field, gaintable=[bandpass_table,scaled_phase_table], gainfield=['0','1'], calwt=F)
