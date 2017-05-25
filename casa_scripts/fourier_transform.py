import sys

spw_range = sys.argv[-6]
output_path = sys.argv[-5]
cal_mode = sys.argv[-4]
loop_count = sys.argv[-3]
ms_dataset = sys.argv[-2]
field_name = sys.argv[-1]

for spw in spw_range.split(","):
    image_path = '{0}/self_cal_image'.format(output_path)
    model_name = "{0}_{1}_{2}_spw{3}.model".format(image_path, cal_mode, loop_count, spw)
    ft(vis=ms_dataset, field=field_name, spw=spw, model=model_name)
