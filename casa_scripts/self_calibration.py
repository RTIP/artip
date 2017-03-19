import sys
import distutils.util
import re
import time

dataset = sys.argv[-20]
image_output_path = sys.argv[-19]
outputvis = sys.argv[-18]
solint = sys.argv[-17]
refant = sys.argv[-16]
minsnr = float(sys.argv[-15])
output_path = sys.argv[-14]
imsize = int(sys.argv[-13])
cell = sys.argv[-12]
robust = float(sys.argv[-11])
interactive = bool(distutils.util.strtobool(sys.argv[-10]))
niter = int(sys.argv[-9])
clean_threshold = sys.argv[-8]
mask_threshold = sys.argv[-7]
mask_path = sys.argv[-6]
loop_count = {'p': int(sys.argv[-4]), 'ap': int(sys.argv[-5])}
cyclefactor = float(sys.argv[-3])
calmode = sys.argv[-2]
spw = sys.argv[-1]
image_path = "{0}/self_cal_image".format(image_output_path)


def model_for_masking(index):
    model = "{0}_{1}_{2}.model".format(image_path, calmode, index - 1)
    if index == 1:
        model = '{0}/cont_base_image.model'.format(output_path)
        if calmode == 'ap':
            model = "{0}/self_cal_image_p_{1}.model".format(image_output_path.replace('self_caled_ap', 'self_caled_p'),
                                                            loop_count['p'])

    return model


for loop_id in range(1, loop_count[calmode] + 1):
    base_model = model_for_masking(loop_id)
    model_path = "{0}/{1}model{2}".format(image_output_path, calmode, loop_id)
    masked_model_path = "{0}/{1}maskmodel{2}".format(image_output_path, calmode, loop_id)

    if loop_id == 1 and calmode == 'p':
        if mask_path == 'None':
            mask_path = "{0}/{1}mask{2}".format(image_output_path, calmode, loop_id)
            im.open(dataset)
            im.mask(mask=mask_path, image=base_model, threshold=mask_threshold)
            im.close()
    else:
        mask_path = "{0}/{1}mask{2}".format(image_output_path, calmode, loop_id)
        im.open(dataset)
        im.mask(mask=mask_path, image=base_model, threshold=mask_threshold)
        im.close()

    ia.open(mask_path)
    ia.setbrightnessunit('Jy/pixel')
    ia.imagecalc(outfile=masked_model_path, pixels='"{0}"*"{1}"'.format(mask_path, base_model))
    ia.close()

    ia.open(masked_model_path)
    ia.setbrightnessunit('Jy/pixel')
    ia.close()

    ft(vis=dataset, field='0', model=masked_model_path)
    cal_table = "{0}/{1}_selfcaltable_{2}.gcal".format(image_output_path, calmode, loop_id)
    image_name = "{0}_{1}_{2}".format(image_path, calmode, loop_id)
    gaincal(vis=dataset, caltable=cal_table, calmode=calmode, solint=solint, refant=refant, minsnr=minsnr)
    applycal(vis=dataset, gaintable=[cal_table], applymode='calonly')

    clean(vis=dataset, imagename=image_name, imagermode='csclean', imsize=imsize, cell=[cell],
          mode='mfs', robust=robust, weighting='briggs', interactive=interactive, threshold=clean_threshold,
          niter=niter, cyclefactor=cyclefactor)

split(vis=dataset, outputvis=outputvis, spw=spw, datacolumn='corrected')
