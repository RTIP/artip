#    How to run this script?
# >> casapy -c sample_casa_script.py


#Import
importgmrt(fitsfile = "/Users/dollyg/Projects/IUCAA/data/30_071_14MAY.FITS", vis = "may14.ms")

#Summary of the data; set-up; scan summary
ms.open("may14.ms")
ms.summary()
ms.close()

#Scan summary
listobs(vis='may14.ms')

#
plotms(vis='may14.ms', xaxis='time',yaxis='amp',correlation='RR,LL', avgchannel='1',spw='0:20', field='0', coloraxis='field')

#
flagdata(vis='may14.ms', antenna='1,19', mode='manual')
#
setjy(vis='may14.ms', field='0', spw='0', modimage='/Applications/CASA.app/Contents/data/nrao/VLA/CalModels/3C48_L.im')
#2016-08-10 12:54:45 INFO imager    Scaling spw(s) [0]'s model image by channel to  I = 16.0782, 16.0597, 16.0412 Jy @(1.41378e+09, 1.41586e+09, 1.41795e+09)Hz (LSRK) for visibility prediction (a few representative values are shown).
#

# gaincal(vis='may14.ms', caltable='bpphase.gcal', field='0', refant='1', calmode='p', solint='int', minsnr=2.0)
gaincal(vis='may14.ms', caltable='bpphase.gcal', field='0', refant='2', calmode='ap', solint='int', minsnr=2.0, spw='0:100')
#
bandpass(vis='may14.ms',caltable='bandpass.bcal',field='0', refant='2', solint='inf', solnorm=T, gaintable=['bpphase.gcal'])
#
plotcal(caltable='bandpass.bcal', xaxis='chan', yaxis='amp', iteration='antenna', subplot=331)
plotcal(caltable='flux.cal', xaxis='antenna', yaxis='amp', subplot=331)
#
gaincal(vis='may14.ms',caltable='intphase.gcal', field='0,1', spw='0:100', refant='2', calmode='p', solint='60s', minsnr=2.0)
#
gaincal(vis='may14.ms', caltable='scanphase.gcal', field='0,1', spw='0:100', refant='2', calmode='p', solint='inf', minsnr=2.0)
#
#
gaincal(vis='may14.ms', caltable='amp.gcal', field='0,1', spw='0:100', refant='2', calmode='ap', solint='inf', minsnr=2.0, gaintable=['bandpass.bcal','intphase.gcal'])
#
fluxscale(vis='may14.ms',caltable='amp.gcal', fluxtable='flux.cal', reference='0')
#2016-08-10 13:05:16 INFO fluxscale     Flux density for 0334-401 in SpW=0 (freq=1.4159e+09 Hz) is: 1.36825 +/- 0.0171359 (SNR = 79.8468, N = 56)
#
#Apply gains to band/flux-cal
applycal(vis='may14.ms', field='0', gaintable=['bandpass.bcal','intphase.gcal','flux.cal'], gainfield=['0','0','0'], calwt=F)
#Apply gains to gain-cal
applycal(vis='may14.ms', field='1', gaintable=['bandpass.bcal','intphase.gcal','flux.cal'], gainfield=['0','1','1'], calwt=F)
#Apply gains to target
applycal(vis='may14.ms', field='2', gaintable=['bandpass.bcal','intphase.gcal','flux.cal'], gainfield=['0','1','1'], calwt=F)
#
#plot single channel calibrated datasets for flux cal, phase cal and source.
plotms(vis='may14.ms', field='0', ydatacolumn='corrected', xaxis='time', yaxis='amp', correlation='RR,LL', spw='0:100', antenna='', coloraxis='antenna1')
plotms(vis='may14.ms', field='1', ydatacolumn='corrected', xaxis='time', yaxis='amp', correlation='RR,LL', spw='0:100', antenna='', coloraxis='antenna1')
plotms(vis='may14.ms', field='2', ydatacolumn='corrected', xaxis='time', yaxis='amp', correlation='RR,LL', spw='0:20', antenna='', coloraxis='antenna1')
#
split(vis='may14.ms', outputvis='j0309calib.ms', field='2')   #line dataset
#
#Create continuum dataset
split(vis='j0309calib.ms', outputvis='j0309cont.ms', field='0', datacolumn='data', spw='0:80~120', width=[41])
#
plotms(vis='j0309cont.ms', field='0', xaxis='time', yaxis='amp', correlation='RR,LL', antenna='', coloraxis='antenna1')
#
#Image and clean
clean(vis='j0309cont.ms', imagename='j0309conti', imagermode='csclean', imsize=256, cell=['0.5arcsec'], mode='mfs', weighting='briggs', robust=0.5, interactive=F, niter=100)

#IN CASA-VIEWER open the image j0309conti.image
viewer('j0309conti.image')   # This is your first image.