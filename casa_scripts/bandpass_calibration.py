import sys

ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
field = sys.argv[-3]
refant = sys.argv[-2]
minsnr = float(sys.argv[-1])

bpphase_gcal = output_path + "/" + 'bpphase.gcal'
bandpass_table = output_path + "/" + 'bandpass.bcal'

sys.stdout.write("\n##### Started calculating bandpass gains on {0}#####\n".format(ms_dataset))
gaincal(vis=ms_dataset, caltable=bpphase_gcal, field=field, refant=refant, calmode='p', solint='60s', minsnr=minsnr)
sys.stdout.write("\n##### Finished calculating bandpass gains on {0}#####\n".format(ms_dataset))

bandpass(vis=ms_dataset, caltable=bandpass_table, field=field, refant=refant, solint='900s', solnorm=T,
         gaintable=[bpphase_gcal], combine='field')
