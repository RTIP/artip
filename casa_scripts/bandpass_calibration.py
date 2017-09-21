import sys

ms_dataset = sys.argv[-7]
output_path = sys.argv[-6]
field = sys.argv[-5]
refant = sys.argv[-4]
solint = float(sys.argv[-3])
phase_calib_minsnr = float(sys.argv[-2])
phase_calib_solint = float(sys.argv[-1])

bpphase_gcal = output_path + "/" + 'bpphase.gcal'
bandpass_table = output_path + "/" + 'bandpass.bcal'

sys.stdout.write("\n##### Started calculating bandpass gains on {0}#####\n".format(ms_dataset))
gaincal(vis=ms_dataset, caltable=bpphase_gcal, field=field, refant=refant, calmode='p', solint=phase_calib_solint, minsnr=phase_calib_minsnr)
sys.stdout.write("\n##### Finished calculating bandpass gains on {0}#####\n".format(ms_dataset))

bandpass(vis=ms_dataset, caltable=bandpass_table, field=field, refant=refant, solint=solint, solnorm=T,
         gaintable=[bpphase_gcal], combine='field')
