channels_to_avg = sys.argv[-7]
ms_dataset = sys.argv[-6]
output_dataset = sys.argv[-5]
field = sys.argv[-4]
datacolumn = sys.argv[-3]
width = [int(v) for v in sys.argv[-2].split(',')]

if sys.argv[-1] == 'all':
    spw = ''
else:
    spw_chan_list = ["{0}:{1}".format(sys.argv[-1], chan) for chan in channels_to_avg.split(',')]
    spw = ','.join(map(str, spw_chan_list))

split(vis=ms_dataset, outputvis=output_dataset, field=field, spw=spw, width=width, datacolumn=datacolumn)
