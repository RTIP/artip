import sys
import distutils.util

dataset = sys.argv[-7]
output_path = sys.argv[-6]
imsize = int(sys.argv[-5])
cell = sys.argv[-4]
robust = float(sys.argv[-3])
interactive = bool(distutils.util.strtobool(sys.argv[-2]))
niter = int(sys.argv[-1])
dirty_image_name = '{0}/cont_dirty_image'.format(output_path)
cont_base_image = '{0}/cont_base_image'.format(output_path)
mask_path = '{0}/mask0'.format(output_path)

clean(vis=dataset, imagename=dirty_image_name, imagermode='csclean', imsize=imsize, cell=[cell], mode='mfs',
      weighting='briggs', robust=robust, interactive=interactive, niter=0)

im.open(dataset)
im.mask(mask=mask_path, image='{0}.image'.format(dirty_image_name), threshold='0.020')
im.close()

ia.open(mask_path)
ia.setbrightnessunit('Jy/beam')
ia.close()

clean(vis=dataset, imagename=cont_base_image, imagermode='csclean', imsize=imsize, cell=[cell], mode='mfs',
      weighting='briggs', robust=robust, interactive=interactive, niter=niter, mask=mask_path)
