import sys

source_id = sys.argv[-5]
ms_dataset = sys.argv[-4]
output_path = sys.argv[-3]
p_loop_count = sys.argv[-2]
ap_loop_count = sys.argv[-1]

p_table = '{0}/self_caled_p_{1}/p_selfcaltable_{2}.gcal'.format(output_path, source_id, p_loop_count)
ap_table = '{0}/self_caled_ap_{1}/ap_selfcaltable_{2}.gcal'.format(output_path, source_id,  ap_loop_count)

applycal(vis=ms_dataset, field='0', gaintable=[p_table, ap_table],
         gainfield=['0', '0'], calwt=F)
