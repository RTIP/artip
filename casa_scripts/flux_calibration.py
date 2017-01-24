import sys

ms_dataset = sys.argv[-2]
output_path = sys.argv[-1]
field = '0'
caltable = output_path + "/" + 'fluxcal.table'
refant = '2'
spw = '0:100'

gaincal(vis=ms_dataset, caltable=caltable, field=field, refant=refant, calmode='ap', solint='2', minsnr=2.0, spw=spw)
applycal(vis=ms_dataset, field=field, gaintable=[caltable], gainfield=[field], calwt=F)
