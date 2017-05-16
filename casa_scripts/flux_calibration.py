import sys

run_count = int(sys.argv[-7])
ms_dataset = sys.argv[-6]
output_path = sys.argv[-5]
field = sys.argv[-4]
refant = sys.argv[-3]
spw = sys.argv[-2]
minsnr = float(sys.argv[-1])

intphase_caltable = output_path + "/" + 'intphase.gcal'
intphase2_caltable = output_path + "/" + 'intphase{0}.gcal'.format(run_count)
amp_caltable = output_path + "/" + 'amp.gcal'
amp2_caltable = output_path + "/" + 'amp{0}.gcal'.format(run_count)
bandpass_bcal = output_path + "/" + 'bandpass.bcal'

if run_count > 1:
    sys.stdout.write("\n##### Started calculating intphase gains on Flux calibrator after bandpass calibration #####\n")
    gaincal(vis=ms_dataset, caltable=intphase2_caltable, field=field, spw=spw, refant=refant, calmode='p',
            solint='60s',
            minsnr=2.0, gaintable=bandpass_bcal)
    sys.stdout.write("\n##### Finished calculating intphase gains on Flux calibrator after bandpass calibration #####\n")

    sys.stdout.write("\n##### Started calculating amp gains on Flux calibrator after bandpass calibration #####\n")
    gaincal(vis=ms_dataset, caltable=amp2_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
            minsnr=2.0, gaintable=[intphase2_caltable, bandpass_bcal])
    sys.stdout.write("\n##### Finished calculating amp gains on Flux calibrator after bandpass calibration #####\n")

    applycal(vis=ms_dataset, field=field, gaintable=[bandpass_bcal, intphase2_caltable, amp2_caltable],
             gainfield=[field, field, field], calwt=F, applymode='calonly')
else:
    sys.stdout.write("\n##### Started calculating intphase gains on Flux calibrator #####\n")
    gaincal(vis=ms_dataset, caltable=intphase_caltable, field=field, spw=spw, refant=refant, calmode='p', solint='60s',
            minsnr=minsnr)
    sys.stdout.write("\n##### Finished calculating intphase gains on Flux calibrator #####\n")

    sys.stdout.write("\n##### Started calculating amp gains on Flux calibrator #####\n")
    gaincal(vis=ms_dataset, caltable=amp_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
            minsnr=minsnr, gaintable=[intphase_caltable])
    sys.stdout.write("\n##### Finished calculating amp gains on Flux calibrator #####\n")
    applycal(vis=ms_dataset, field=field, gaintable=[intphase_caltable, amp_caltable], gainfield=[field, field],
             calwt=F)
