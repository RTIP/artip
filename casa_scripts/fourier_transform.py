import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

spw_range = parameters[0]
output_path = parameters[1]
cal_mode = parameters[2]
loop_count = parameters[3]
ms_dataset = parameters[4]
field_name = parameters[5]

image_path = '{0}/self_cal_image'.format(output_path)
model_name = "{0}_{1}_{2}.model".format(image_path, cal_mode, loop_count)
ft(vis=ms_dataset, field=field_name, spw=spw_range, model=model_name)
