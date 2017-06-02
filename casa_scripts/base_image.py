import sys
import distutils.util
import yaml


def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs


BASE_IMAGE_CONFIGS = load("conf/imaging_config.yml")["base_image"]

dataset = sys.argv[-2]
output_path = sys.argv[-1]
cont_base_image = '{0}/cont_base_image'.format(output_path)

imsize = BASE_IMAGE_CONFIGS['imsize']
cell = BASE_IMAGE_CONFIGS['cell']
stokes = BASE_IMAGE_CONFIGS['stokes']
weighting = BASE_IMAGE_CONFIGS['weighting']
robust = BASE_IMAGE_CONFIGS['robust']
restoringbeam = BASE_IMAGE_CONFIGS['restoringbeam']
uvtaper = BASE_IMAGE_CONFIGS['uvtaper']
mask = BASE_IMAGE_CONFIGS['mask']
interactive = bool(distutils.util.strtobool(BASE_IMAGE_CONFIGS['interactive']))
niter = BASE_IMAGE_CONFIGS['niter']
deconvolver = BASE_IMAGE_CONFIGS['deconvolver']
specmode = BASE_IMAGE_CONFIGS['specmode']
nterms = BASE_IMAGE_CONFIGS['nterms']
reffreq = BASE_IMAGE_CONFIGS['reffreq']
nchan = BASE_IMAGE_CONFIGS['nchan']
start = BASE_IMAGE_CONFIGS['start']
width = BASE_IMAGE_CONFIGS['width']
outframe = BASE_IMAGE_CONFIGS['outframe']
veltype = BASE_IMAGE_CONFIGS['veltype']
restfreq = BASE_IMAGE_CONFIGS['restfreq']
gridder = BASE_IMAGE_CONFIGS['gridder']
facets = BASE_IMAGE_CONFIGS['facets']
wprojplanes = BASE_IMAGE_CONFIGS['wprojplanes']
aterm = BASE_IMAGE_CONFIGS['aterm']
psterm = BASE_IMAGE_CONFIGS['psterm']
wbawp = BASE_IMAGE_CONFIGS['wbawp']
conjbeams = BASE_IMAGE_CONFIGS['conjbeams']
pblimit = BASE_IMAGE_CONFIGS['pblimit']
normtype = BASE_IMAGE_CONFIGS['normtype']
pbcor = BASE_IMAGE_CONFIGS['pbcor']
gain = BASE_IMAGE_CONFIGS['gain']
threshold = BASE_IMAGE_CONFIGS['threshold']
cycleniter = BASE_IMAGE_CONFIGS['cycleniter']
cyclefactor = BASE_IMAGE_CONFIGS['cyclefactor']
savemodel = BASE_IMAGE_CONFIGS['savemodel']
parallel = BASE_IMAGE_CONFIGS['parallel']

tclean(vis=dataset, imagename=cont_base_image, imsize=imsize, cell=[cell], stokes=stokes, weighting=weighting,
       robust=robust, restoringbeam=restoringbeam, uvtaper=uvtaper, mask=mask, interactive=interactive, niter=niter,
       deconvolver=deconvolver, specmode=specmode, nterms=nterms, reffreq=reffreq, nchan=nchan, start=start,
       width=width, outframe=outframe, veltype=veltype, restfreq=restfreq, gridder=gridder, facets=facets,
       wprojplanes=wprojplanes, aterm=aterm, psterm=psterm, wbawp=wbawp, conjbeams=conjbeams, pblimit=pblimit,
       normtype=normtype, pbcor=pbcor, gain=gain, threshold=threshold, cycleniter=cycleniter, cyclefactor=cyclefactor,
       savemodel=savemodel, parallel=parallel)