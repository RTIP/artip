import sys

ms_dataset = sys.argv[-4]
spw = sys.argv[-3]
output_dataset = sys.argv[-2]
datacolumn = sys.argv[-1]

split(vis=ms_dataset, outputvis=output_dataset, datacolumn=datacolumn, spw=spw)
