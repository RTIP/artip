import sys

ms_dataset = sys.argv[-2]
output_path = sys.argv[-1]
field = '0'
intphase_caltable = output_path + "/" + 'intphase.gcal'
amp_caltable = output_path + "/" + 'amp.gcal'
refant = '3'
spw = '0:100'

gaincal(vis=ms_dataset, caltable=intphase_caltable, field=field, spw=spw, refant=refant, calmode='p', solint='60s',
        minsnr=2.0)
gaincal(vis=ms_dataset, caltable=amp_caltable, field=field, spw=spw, refant=refant, calmode='ap', solint='inf',
        minsnr=2.0, gaintable=[intphase_caltable])
applycal(vis=ms_dataset, field=field, gaintable=[intphase_caltable, amp_caltable], gainfield=[field, field], calwt=F)
