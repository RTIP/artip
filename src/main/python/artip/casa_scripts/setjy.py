import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

spw = parameters[0]
ms_dataset = parameters[1]
field = parameters[2]
model_path = parameters[3]

setjy(vis=ms_dataset, field=field, spw=spw, modimage=model_path, usescratch=True)