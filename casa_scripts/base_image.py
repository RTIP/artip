import sys
import distutils.util

dataset = sys.argv[-9]
output_path = sys.argv[-8]
imsize = int(sys.argv[-7])
cell = sys.argv[-6]
robust = float(sys.argv[-5])
threshold = sys.argv[-4]
interactive = bool(distutils.util.strtobool(sys.argv[-3]))
niter = int(sys.argv[-2])
cyclefactor = float(sys.argv[-1])
cont_base_image = '{0}/cont_base_image'.format(output_path)

clean(vis=dataset, imagename=cont_base_image, imagermode='csclean', imsize=imsize, cell=[cell], mode='mfs',
      weighting='briggs', robust=robust, interactive=interactive, threshold=threshold, niter=niter,
      cyclefactor=cyclefactor)
