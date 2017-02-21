import sys

ms_dataset = sys.argv[-4]
output_path = sys.argv[-3]
p_loop_count = sys.argv[-2]
ap_loop_count = sys.argv[-1]

p_table = '{0}/continuum/self_caled_p/p_selfcaltable_{1}.gcal'.format(output_path, p_loop_count)
ap_table = '{0}/continuum/self_caled_p/self_caled_ap/ap_selfcaltable_{1}.gcal'.format(output_path, ap_loop_count)

applycal(vis=ms_dataset, field='0', gaintable=[p_table, ap_table],
         gainfield=['0', '0'], calwt=F)
