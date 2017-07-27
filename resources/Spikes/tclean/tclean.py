import sys
import distutils.util

dataset = sys.argv[-3]
parallel = bool(distutils.util.strtobool(sys.argv[-2]))
image_name = sys.argv[-1]
tclean(vis=dataset, imagename=image_name, imsize=128, cell=['0.5arcsec'], stokes='I', weighting='briggs', robust=0.5, restoringbeam='', uvtaper='', mask='', interactive=F, niter=0, deconvolver='hogbom', specmode='cube', nterms=1, reffreq='', nchan=-1, start='', width='', outframe='topo', veltype='', restfreq='', gridder='standard', facets=1, wprojplanes=1, aterm=True, psterm=False, wbawp=False, conjbeams=True, pblimit=0.2, normtype='flatnoise', pbcor=False, gain=0.1, threshold='10.0mJy', cycleniter=-1, cyclefactor=1.0, savemodel='none', parallel=parallel, spw='0')
