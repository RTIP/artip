import sys
import distutils.util
import yaml

spw_list = sys.argv[-3]
ms_input = sys.argv[-2]
image_path = sys.argv[-1]
field = '0'

image_name = "{0}/line_spectral_image".format(image_path)
corrected_line_ms = "{0}/corrected_line.ms".format(image_path)


def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs


IMAGE_CONFIGS = load("conf/imaging_config.yml")["line_image"]
imsize = IMAGE_CONFIGS['imsize']
fitspw_channels = IMAGE_CONFIGS['fitspw_channels']
fitspw = ",".join(["{0}:{1}".format(s, fitspw_channels) for s in spw_list.split(",")])
cell = IMAGE_CONFIGS['cell']
stokes = IMAGE_CONFIGS['stokes']
weighting = IMAGE_CONFIGS['weighting']
robust = IMAGE_CONFIGS['robust']
restoringbeam = IMAGE_CONFIGS['restoringbeam']
uvtaper = IMAGE_CONFIGS['uvtaper']
mask = IMAGE_CONFIGS['mask']
interactive = bool(distutils.util.strtobool(IMAGE_CONFIGS['interactive']))
niter = IMAGE_CONFIGS['niter']
deconvolver = IMAGE_CONFIGS['deconvolver']
specmode = IMAGE_CONFIGS['specmode']
nterms = IMAGE_CONFIGS['nterms']
reffreq = IMAGE_CONFIGS['reffreq']
nchan = IMAGE_CONFIGS['nchan']
start = IMAGE_CONFIGS['start']
width = IMAGE_CONFIGS['width']
outframe = IMAGE_CONFIGS['outframe']
veltype = IMAGE_CONFIGS['veltype']
restfreq = IMAGE_CONFIGS['restfreq']
gridder = IMAGE_CONFIGS['gridder']
facets = IMAGE_CONFIGS['facets']
wprojplanes = IMAGE_CONFIGS['wprojplanes']
aterm = IMAGE_CONFIGS['aterm']
psterm = IMAGE_CONFIGS['psterm']
wbawp = IMAGE_CONFIGS['wbawp']
conjbeams = IMAGE_CONFIGS['conjbeams']
pblimit = IMAGE_CONFIGS['pblimit']
normtype = IMAGE_CONFIGS['normtype']
pbcor = IMAGE_CONFIGS['pbcor']
gain = IMAGE_CONFIGS['gain']
threshold = IMAGE_CONFIGS['threshold']
cycleniter = IMAGE_CONFIGS['cycleniter']
cyclefactor = IMAGE_CONFIGS['cyclefactor']
savemodel = IMAGE_CONFIGS['savemodel']
parallel = IMAGE_CONFIGS['parallel']

split(vis=ms_input, outputvis=corrected_line_ms, spw=spw_list, datacolumn='corrected')

uvcontsub(vis=corrected_line_ms, field=field, spw=spw_list, fitspw=fitspw, solint='int', fitorder=0)

tclean(vis="{0}.contsub".format(corrected_line_ms), imagename=image_name, imsize=imsize, cell=[cell], stokes=stokes,
       weighting=weighting,
       robust=robust, restoringbeam=restoringbeam, uvtaper=uvtaper, mask=mask, interactive=interactive, niter=niter,
       deconvolver=deconvolver, specmode=specmode, nterms=nterms, reffreq=reffreq, nchan=nchan, start=start,
       width=width, outframe=outframe, veltype=veltype, restfreq=restfreq, gridder=gridder, facets=facets,
       wprojplanes=wprojplanes, aterm=aterm, psterm=psterm, wbawp=wbawp, conjbeams=conjbeams, pblimit=pblimit,
       normtype=normtype, pbcor=pbcor, gain=gain, threshold=threshold, cycleniter=cycleniter, cyclefactor=cyclefactor,
       savemodel=savemodel, parallel=parallel, spw=spw_list)
