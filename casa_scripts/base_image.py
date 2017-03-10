import sys
import distutils.util

dataset = sys.argv[-8]
output_path = sys.argv[-7]
imsize = int(sys.argv[-6])
cell = sys.argv[-5]
robust = float(sys.argv[-4])
threshold = sys.argv[-3]
interactive = bool(distutils.util.strtobool(sys.argv[-2]))
niter = int(sys.argv[-1])
cont_base_image = '{0}/cont_base_image'.format(output_path)

clean(vis=dataset, imagename=cont_base_image, imagermode='csclean', imsize=imsize, cell=[cell], mode='mfs',
      weighting='briggs', robust=robust, interactive=interactive, threshold=threshold, niter=niter)
