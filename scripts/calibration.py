import sys

ms_dataset = sys.argv[3]
field='0'
caltable = 'fluxcal.table'
refant='2'
spw='0:100'
antennas_to_be_flagged = '1,18'

flagdata(vis=ms_dataset, mode='unflag')
flagdata(vis=ms_dataset, antenna=antennas_to_be_flagged, mode='manual')
gaincal(vis=ms_dataset, caltable=caltable, field=field, refant=refant, calmode='ap', solint='2', minsnr=2.0, spw=spw)
applycal(vis=ms_dataset, field=field, gaintable=[caltable], gainfield=[field], calwt=F)
