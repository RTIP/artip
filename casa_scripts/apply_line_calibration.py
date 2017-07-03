import sys

p_loop_count = sys.argv[-5]
ap_loop_count = sys.argv[-4]
ap_table = sys.argv[-3]
p_table = sys.argv[-2]
ms_dataset = sys.argv[-1]

gaintable = []
gaintable.append(p_table) if p_loop_count > 0
gaintable.append(ap_table) if ap_loop_count > 0

gainfield = ['0'] * len(gaintable)

applycal(vis=ms_dataset, field='0', gaintable=gaintable,
         gainfield=gainfield, calwt=F)
