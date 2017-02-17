import sys
import distutils.util

dataset = sys.argv[-11]
solint = sys.argv[-10]
refant = sys.argv[-9]
minsnr = float(sys.argv[-8])
image_prefix = sys.argv[-7]
imsize = int(sys.argv[-6])
cell = sys.argv[-5]
robust = float(sys.argv[-4])
interactive = bool(distutils.util.strtobool(sys.argv[-3]))
niter = int(sys.argv[-2])
loop_count = int(sys.argv[-1])

for loop_id in range(0, loop_count):
    cal_table = "pselfcaltable_{0}.gcal".format(loop_id)
    image_name = "{0}_{1}".format(image_prefix, loop_id)
    gaincal(vis=dataset, caltable=cal_table, calmode='p', solint=solint, refant=refant,
            minsnr=minsnr)
    applycal(vis=dataset, gaintable=[cal_table])

    clean(vis=dataset, imagename=image_name, imagermode='csclean', imsize=imsize,
          cell=[cell], mode='mfs', weighting='briggs', robust=robust, interactive=interactive,
          niter=niter)
