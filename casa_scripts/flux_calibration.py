import sys

ms_dataset = sys.argv[-6]
output_path = sys.argv[-5]
field = sys.argv[-4]
refant = sys.argv[-3]
spw = sys.argv[-2]
minsnr = float(sys.argv[-1])

intphase_caltable = output_path + "/" + 'intphase.gcal'
amp_caltable = output_path + "/" + 'amp.gcal'

gaincal(vis=ms_dataset, caltable=intphase_caltable, field=field, spw=spw, refant=refant, calmode='p', solint='60s',
        minsnr=minsnr)
gaincal(vis=ms_dataset, caltable=amp_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
        minsnr=minsnr, gaintable=[intphase_caltable])
applycal(vis=ms_dataset, field=field, gaintable=[intphase_caltable, amp_caltable], gainfield=[field, field], calwt=F)
