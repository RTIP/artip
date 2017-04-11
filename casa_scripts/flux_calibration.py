import sys

run_with_bandpass = sys.argv[-7]
ms_dataset = sys.argv[-6]
output_path = sys.argv[-5]
field = sys.argv[-4]
refant = sys.argv[-3]
spw = sys.argv[-2]
minsnr = float(sys.argv[-1])

intphase_caltable = output_path + "/" + 'intphase.gcal'
intphase2_caltable = output_path + "/" + 'intphase2.gcal'
amp_caltable = output_path + "/" + 'amp.gcal'
amp2_caltable = output_path + "/" + 'amp2.gcal'
bandpass_bcal = output_path + "/" + 'bandpass.bcal'

if run_with_bandpass == "True":
    gaincal(vis=ms_dataset, caltable=intphase2_caltable, field=field, spw=spw, refant=refant, calmode='p',
            solint='60s',
            minsnr=2.0, gaintable=bandpass_bcal)
    gaincal(vis=ms_dataset, caltable=amp2_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
            minsnr=2.0, gaintable=[intphase2_caltable, bandpass_bcal])
    applycal(vis=ms_dataset, field=field, gaintable=[bandpass_bcal, intphase2_caltable, amp2_caltable],
             gainfield=[field, field, field], calwt=F, applymode='calonly')
else:
    gaincal(vis=ms_dataset, caltable=intphase_caltable, field=field, spw=spw, refant=refant, calmode='p', solint='60s',
            minsnr=minsnr)
    gaincal(vis=ms_dataset, caltable=amp_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
            minsnr=minsnr, gaintable=[intphase_caltable])
    applycal(vis=ms_dataset, field=field, gaintable=[intphase_caltable, amp_caltable], gainfield=[field, field],
             calwt=F)
