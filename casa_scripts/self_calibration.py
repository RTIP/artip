import sys
import distutils.util

dataset = sys.argv[-15]
image_output_path = sys.argv[-14]
outputvis = sys.argv[-13]
solint = sys.argv[-12]
refant = sys.argv[-11]
minsnr = float(sys.argv[-10])
output_path = sys.argv[-9]
imsize = int(sys.argv[-8])
cell = sys.argv[-7]
robust = float(sys.argv[-6])
interactive = bool(distutils.util.strtobool(sys.argv[-5]))
niter = int(sys.argv[-4])
loop_count = int(sys.argv[-3])
calmode = sys.argv[-2]
spw = sys.argv[-1]
image_path = "{0}/self_cal_image".format(image_output_path)

for loop_id in range(0, loop_count):
    cal_table = "{0}/{1}_selfcaltable_{2}.gcal".format(image_output_path, calmode, loop_id+1)
    image_name = "{0}_{1}_{2}".format(image_path, calmode, loop_id+1)
    gaincal(vis=dataset, caltable=cal_table, calmode=calmode, solint=solint, refant=refant,
            minsnr=minsnr)
    applycal(vis=dataset, gaintable=[cal_table])

    clean(vis=dataset, imagename=image_name, imagermode='csclean', imsize=imsize,
          cell=[cell], mode='mfs', weighting='briggs', robust=robust, interactive=interactive,
          niter=niter)

split(vis=dataset, outputvis=outputvis, spw=spw, datacolumn='corrected')
