import sys
import os

ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
flux_cal_field = sys.argv[-3]
phase_cal_field = sys.argv[-2]
channels_to_average = sys.argv[-1]
spw = "0:{0}".format(channels_to_average)
refant = '3'

intphase_gcal = output_path + "/" + 'intphase.gcal'
tmp_intphase_gcal = output_path + "/" + 'intphase_tmp.gcal'
bandpass_bcal = output_path + "/" + 'bandpass.bcal'
amp_gcal = output_path + "/" + 'amp.gcal'
tmp_amp_gcal = output_path + "/" + 'amp_tmp.gcal'
scanphase_gcal = output_path + "/" + 'scanphase.gcal'
flux_gcal = output_path + "/" + 'flux.gcal'

os.system("cp -r {0} {1}".format(intphase_gcal, tmp_intphase_gcal))
os.system("cp -r {0} {1}".format(amp_gcal, tmp_amp_gcal))

gaincal(vis=ms_dataset, caltable=tmp_intphase_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='p',
        solint='60s', minsnr=2.0, append=True)
gaincal(vis=ms_dataset, caltable=tmp_amp_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='ap', solint='inf',
        minsnr=2.0, gaintable=[tmp_intphase_gcal], append=True)
gaincal(vis=ms_dataset, caltable=scanphase_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='p',
        solint='inf', minsnr=2.0)
fluxscale(vis=ms_dataset, caltable=tmp_amp_gcal, fluxtable=flux_gcal, reference=flux_cal_field)
applycal(vis=ms_dataset, field=phase_cal_field, gaintable=[tmp_intphase_gcal, tmp_amp_gcal],
         gainfield=[flux_cal_field, phase_cal_field, phase_cal_field], calwt=F)

os.system("rm -r {0}".format(tmp_intphase_gcal))
os.system("rm -r {0}".format(tmp_amp_gcal))