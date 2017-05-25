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

for spw in spw_list.split(","):
    fitspw = "0:{0}".format(spw, fitspw_channels)
    image_name = "{0}/line_spectral_image_spw{1}".format(image_path, spw)
    spw_line_ms = "{0}/line_spw{1}.ms".format(image_path, spw)
    split(vis=ms_input, outputvis=spw_line_ms, spw=spw, datacolumn='corrected')
    uvcontsub(vis=spw_line_ms, field=field, spw='0', fitspw=fitspw, solint='int', fitorder=0)
    clean(vis="{0}.contsub".format(spw_line_ms), imagename=image_name, imagermode='csclean', imsize=imsize, cell=[cell],
          mode='channel', weighting='briggs', robust=robust, threshold=threshold, interactive=interactive, niter=niter,
          spw='0')
