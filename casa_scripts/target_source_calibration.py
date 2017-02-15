import sys

ms_dataset = sys.argv[-3]
output_path = sys.argv[-2]
field = sys.argv[-1]

bandpass_table = output_path + "/" + 'bandpass.bcal'
scanphase_gcal = output_path + "/" + 'scanphase.gcal'
amp_gcal = output_path + "/" + 'amp.gcal'

applycal(vis=ms_dataset, field=field, gaintable=[bandpass_table, scanphase_gcal, amp_gcal],
         gainfield=['0', '1', '1'], calwt=F)