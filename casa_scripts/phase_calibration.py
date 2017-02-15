import sys
import os

ms_dataset = sys.argv[-7]
output_path = sys.argv[-6]
flux_cal_field = sys.argv[-5]
phase_cal_field = sys.argv[-4]
spw = sys.argv[-3]
refant = sys.argv[-2]
minsnr = float(sys.argv[-1])

intphase_gcal = output_path + "/" + 'intphase.gcal'
tmp_intphase_gcal = output_path + "/" + 'intphase_tmp.gcal'  # This is done to keep empty phase gains in intphase.gcal because "append=True" in gaincal throws an error[duplicate phase gains at same time] in subsequent phase calibration run.

amp_gcal = output_path + "/" + 'amp.gcal'
tmp_amp_gcal = output_path + "/" + 'amp_tmp.gcal'  # same reason as above

bandpass_bcal = output_path + "/" + 'bandpass.bcal'
scanphase_gcal = output_path + "/" + 'scanphase.gcal'
flux_gcal = output_path + "/" + 'flux.gcal'

# copying intphase_gcal to a tmp intphase_gcal and will apply gains using the tmp gcal tables
os.system("cp -r {0} {1}".format(intphase_gcal, tmp_intphase_gcal))
os.system("cp -r {0} {1}".format(amp_gcal, tmp_amp_gcal))

gaincal(vis=ms_dataset, caltable=tmp_intphase_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='p',
        solint='60s', minsnr=minsnr, append=True)
gaincal(vis=ms_dataset, caltable=tmp_amp_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='ap',
        solint='inf', minsnr=minsnr, gaintable=[tmp_intphase_gcal], append=True)
gaincal(vis=ms_dataset, caltable=scanphase_gcal, field=phase_cal_field, spw=spw, refant=refant, calmode='p',
        solint='inf', minsnr=minsnr)
fluxscale(vis=ms_dataset, caltable=tmp_amp_gcal, fluxtable=flux_gcal, reference=flux_cal_field)
applycal(vis=ms_dataset, field=phase_cal_field, gaintable=[bandpass_bcal, tmp_intphase_gcal, tmp_amp_gcal],
         gainfield=[flux_cal_field, phase_cal_field, phase_cal_field], calwt=F)

os.system("rm -r {0}".format(tmp_intphase_gcal))
os.system("rm -r {0}".format(tmp_amp_gcal))
