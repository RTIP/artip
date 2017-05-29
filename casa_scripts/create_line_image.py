import sys
import distutils.util

spw_list = sys.argv[-11]
fitspw_channels = sys.argv[-10]
ms_input = sys.argv[-9]
image_path = sys.argv[-8]
model = sys.argv[-7]
threshold = sys.argv[-6]
imsize = int(sys.argv[-5])
interactive = bool(distutils.util.strtobool(sys.argv[-4]))
robust = float(sys.argv[-3])
cell = sys.argv[-2]
niter = int(sys.argv[-1])
field = '0'

fitspw = ",".join(["{0}:{1}".format(s, fitspw_channels) for s in spw_list.split(",")])

image_name = "{0}/line_spectral_image".format(image_path)
corrected_line_ms = "{0}/corrected_line.ms".format(image_path)
split(vis=ms_input, outputvis=corrected_line_ms, spw=spw_list, datacolumn='corrected')
uvcontsub(vis=corrected_line_ms, field=field, spw=spw_list, fitspw=fitspw, solint='int', fitorder=0)
clean(vis="{0}.contsub".format(corrected_line_ms), imagename=image_name, imagermode='csclean', imsize=imsize,
      cell=[cell], mode='channel', weighting='briggs', robust=robust, threshold=threshold, interactive=interactive,
      niter=niter, spw=spw_list)
