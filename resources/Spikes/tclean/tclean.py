import sys
import distutils.util

dataset = sys.argv[-3]
parallel = bool(distutils.util.strtobool(sys.argv[-2]))
image_name = sys.argv[-1]

tclean(vis=dataset, selectdata=True, field='', spw='', timerange='', uvrange='', antenna='', scan='', observation='',
       intent='', datacolumn='corrected', imagename=image_name, imsize=4096, cell=['0.5arcsec'], phasecenter='',
       stokes='I', projection='SIN', startmodel='', specmode='mfs', reffreq='', nchan=-1, start='', width='',
       outframe='', veltype='', restfreq='', interpolation='linear', gridder='standard', facets=1, chanchunks=1,
       wprojplanes=1, vptable='', aterm=True, psterm=False, wbawp=False, conjbeams=True, cfcache='',
       computepastep=360.0, rotatepastep=360.0, pblimit=0.2, normtype='flatnoise', deconvolver='hogbom', scales=[],
       nterms=1, smallscalebias=0.6, restoration=True, restoringbeam='', pbcor=False, outlierfile='',
       weighting='briggs', robust=0.5, npixels=0, uvtaper='', niter=0, gain=0.1, threshold='10.0mJy', cycleniter=-1,
       cyclefactor=1.0, minpsffraction=0.05, maxpsffraction=0.8, interactive=True, usemask='user', mask='', pbmask=0.0,
       maskthreshold='', maskresolution='', nmask=0, autoadjust=False, sidelobethreshold=3.0, noisethreshold=3.0,
       lownoisethreshold=3.0, smoothfactor=1.0, minbeamfrac=-1.0, cutthreshold=0.01, restart=True,
       savemodel='modelcolumn', calcres=True, calcpsf=True, parallel=parallel)
