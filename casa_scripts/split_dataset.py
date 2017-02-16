ms_dataset = sys.argv[-6]
output_dataset = sys.argv[-5]
field = sys.argv[-4]
datacolumn = sys.argv[-3]
width = int(sys.argv[-2])
if sys.argv[-1] == 'all':
    spw = ''
else:
    spw = sys.argv[-1]

split(vis=ms_dataset, outputvis=output_dataset, field=field, spw=spw, width=width, datacolumn=datacolumn)
