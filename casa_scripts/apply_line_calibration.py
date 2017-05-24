import sys

ap_table = sys.argv[-3]
p_table = sys.argv[-2]
ms_dataset = sys.argv[-1]

applycal(vis=ms_dataset, field='0', gaintable=[p_table, ap_table],
         gainfield=['0', '0'], calwt=F)
