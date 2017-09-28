import sys
import distutils.util
import yaml

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs

config_path = parameters[0]
dataset = parameters[1]
image_output_path = parameters[2]
outputvis = parameters[3]
solint = parameters[4]
refant = parameters[5]
minsnr = float(parameters[6])
output_path = parameters[7]
applymode = parameters[8]
mask_threshold = parameters[9]
bmask_bottom_left_corner = [int(parameters[10]), int(parameters[11])]
bmask_top_right_corner = [int(parameters[12]), int(parameters[13])]
mask_path = parameters[14]
loop_count = {'ap': int(parameters[15]), 'p': int(parameters[16])}
calmode = parameters[17]
spw = parameters[18]

image_path = "{0}/self_cal_image".format(image_output_path)

IMAGE_CONFIGS = load(config_path+"imaging.yml")["cont_image"]

imsize = IMAGE_CONFIGS['imsize']
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
clean_threshold = IMAGE_CONFIGS['threshold']
cycleniter = IMAGE_CONFIGS['cycleniter']
cyclefactor = IMAGE_CONFIGS['cyclefactor']
savemodel = IMAGE_CONFIGS['savemodel']
parallel = IMAGE_CONFIGS['parallel']


def model_for_masking(index):
    model = "{0}_{1}_{2}.model".format(image_path, calmode, index - 1)
    if index == 1:
        model = '{0}/cont_base_image.model'.format(output_path)
        if calmode == 'ap':
            model = "{0}/self_cal_image_p_{1}.model".format(image_output_path.replace('self_caled_ap', 'self_caled_p'),
                                                            loop_count['p'])

    return model


for loop_id in range(1, loop_count[calmode] + 1):
    casalog.post(">>>> Calmode={0} Loop_id={1}".format(calmode, loop_id))
    base_model = model_for_masking(loop_id)
    model_path = "{0}/{1}model{2}".format(image_output_path, calmode, loop_id)
    masked_model_path = "{0}/{1}maskmodel{2}".format(image_output_path, calmode, loop_id)
    bmasked_model_path = "{0}/{1}bmaskmodel{2}".format(image_output_path, calmode, loop_id)

    if loop_id == 1 and calmode == 'p':
        if mask_path == 'None':
            mask_path = "{0}/{1}mask{2}".format(image_output_path, calmode, loop_id)
            box_mask_path = "{0}/{1}bmask{2}".format(image_output_path, calmode, loop_id)
            im.open(dataset)
            im.mask(mask=mask_path, image=base_model, threshold=mask_threshold)
            im.defineimage(nx=imsize, ny=imsize, cellx=cell, celly=cell)
            im.boxmask(mask=box_mask_path, blc=bmask_bottom_left_corner, trc=bmask_top_right_corner)
            im.close()
    else:
        mask_path = "{0}/{1}mask{2}".format(image_output_path, calmode, loop_id)
        box_mask_path = "{0}/{1}bmask{2}".format(image_output_path, calmode, loop_id)
        im.open(dataset)
        im.defineimage(nx=imsize, ny=imsize, cellx=cell, celly=cell)
        im.boxmask(mask=box_mask_path, blc=bmask_bottom_left_corner, trc=bmask_top_right_corner)
        im.mask(mask=mask_path, image=base_model, threshold=mask_threshold)
        im.close()

    ia.open(mask_path)
    ia.setbrightnessunit('Jy/pixel')
    ia.imagecalc(outfile=masked_model_path, pixels='"{0}"*"{1}"'.format(mask_path, base_model))
    ia.close()

    ia.open(box_mask_path)
    ia.setbrightnessunit('Jy/pixel')
    ia.imagecalc(outfile=bmasked_model_path, pixels='"{0}"*"{1}"'.format(box_mask_path, masked_model_path))
    ia.close()

    ia.open(bmasked_model_path)
    ia.setbrightnessunit('Jy/pixel')
    ia.close()

    fill_model_image_name = "{0}_{1}_{2}_fill_masked_model_image".format(image_path, calmode, loop_id)

    # This will fill the model column with masked model.
    # imsize, cell, nterms, wprojplanes, robust, startmodel
    tclean(vis=dataset, imagename=fill_model_image_name, startmodel=bmasked_model_path, imsize=imsize, cell=[cell],
           robust=robust, niter=0, specmode='mfs', nterms=nterms, nchan=nchan, wprojplanes=wprojplanes,
           savemodel='modelcolumn', parallel=parallel)

    cal_table = "{0}/{1}_selfcaltable_{2}.gcal".format(image_output_path, calmode, loop_id)
    image_name = "{0}_{1}_{2}".format(image_path, calmode, loop_id)
    sys.stdout.write(
        "\n##### Started calculating selfcal gains on {0}, loop={1} and calmode={2}#####\n".format(dataset, loop_id,
                                                                                                   calmode))
    gaincal(vis=dataset, caltable=cal_table, calmode=calmode, solint=solint, refant=refant, minsnr=minsnr, spw=spw)
    sys.stdout.write(
        "\n##### Finished calculating selfcal gains on {0}, loop={1} and calmode={2}#####\n".format(dataset, loop_id,
                                                                                                    calmode))
    applycal(vis=dataset, gaintable=[cal_table], applymode=applymode, spw=spw)

    tclean(vis=dataset, imagename=image_name, imsize=imsize, cell=[cell], stokes=stokes, weighting=weighting,
           robust=robust, restoringbeam=restoringbeam, uvtaper=uvtaper, mask=mask, interactive=interactive, niter=niter,
           deconvolver=deconvolver, specmode=specmode, nterms=nterms, reffreq=reffreq, nchan=nchan, start=start,
           width=width, outframe=outframe, veltype=veltype, restfreq=restfreq, gridder=gridder, facets=facets,
           wprojplanes=wprojplanes, aterm=aterm, psterm=psterm, wbawp=wbawp, conjbeams=conjbeams, pblimit=pblimit,
           normtype=normtype, pbcor=pbcor, gain=gain, threshold=clean_threshold, cycleniter=cycleniter,
           cyclefactor=cyclefactor, savemodel=savemodel, parallel=parallel, spw=spw)

split(vis=dataset, outputvis=outputvis, spw=spw, datacolumn='corrected')
