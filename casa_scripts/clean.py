import sys
import distutils.util

dataset = sys.argv[-7]
imagename = sys.argv[-6]
imsize = int(sys.argv[-5])
cell = sys.argv[-4]
robust = float(sys.argv[-3])
interactive = bool(distutils.util.strtobool(sys.argv[-2]))
niter = int(sys.argv[-1])

clean(vis=dataset, imagename=imagename, imagermode='csclean', imsize=imsize,
      cell=[cell], mode='mfs', weighting='briggs', robust=robust, interactive=interactive,
      niter=niter)
