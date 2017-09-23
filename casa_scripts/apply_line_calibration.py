import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

p_loop_count = int(parameters[0])
ap_loop_count = int(parameters[1])
ap_table = parameters[2]
p_table = parameters[3]
ms_dataset = parameters[4]

gaintable = []
if p_loop_count > 0: gaintable.append(p_table)
if ap_loop_count > 0: gaintable.append(ap_table)

gainfield = ['0'] * len(gaintable)

applycal(vis=ms_dataset, field='0', gaintable=gaintable,
         gainfield=gainfield, calwt=F)
