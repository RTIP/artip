import sys
import distutils.util
import re
import time

dataset = sys.argv[-24]
image_output_path = sys.argv[-23]
outputvis = sys.argv[-22]
solint = sys.argv[-21]
refant = sys.argv[-20]
minsnr = float(sys.argv[-19])
output_path = sys.argv[-18]
imsize = int(sys.argv[-17])
cell = sys.argv[-16]
robust = float(sys.argv[-15])
interactive = bool(distutils.util.strtobool(sys.argv[-14]))
niter = int(sys.argv[-13])
clean_threshold = sys.argv[-12]
mask_threshold = sys.argv[-11]
bmask_bottom_left_corner = [int(sys.argv[-10]), int(sys.argv[-9])]
bmask_top_right_corner = [int(sys.argv[-8]), int(sys.argv[-7])]
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

    ft(vis=dataset, field='0', model=bmasked_model_path)
    cal_table = "{0}/{1}_selfcaltable_{2}.gcal".format(image_output_path, calmode, loop_id)
    image_name = "{0}_{1}_{2}".format(image_path, calmode, loop_id)
    sys.stdout.write("\n##### Started calculating selfcal gains on {0}, loop={1} and calmode={2}#####\n".format(dataset, loop_id,
                                                                                                   calmode))
    gaincal(vis=dataset, caltable=cal_table, calmode=calmode, solint=solint, refant=refant, minsnr=minsnr)
    sys.stdout.write("\n##### Finished calculating selfcal gains on {0}, loop={1} and calmode={2}#####\n".format(dataset, loop_id,
                                                                                                   calmode))
    applycal(vis=dataset, gaintable=[cal_table], applymode='calonly')

    clean(vis=dataset, imagename=image_name, imagermode='csclean', imsize=imsize, cell=[cell],
          mode='mfs', robust=robust, weighting='briggs', interactive=interactive, threshold=clean_threshold,
          niter=niter, cyclefactor=cyclefactor)

split(vis=dataset, outputvis=outputvis, spw=spw, datacolumn='corrected')
