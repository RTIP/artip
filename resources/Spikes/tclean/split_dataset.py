import sys

spw = sys.argv[-4]
ms_dataset = sys.argv[-3]
output_dataset = sys.argv[-2]
datacolumn = sys.argv[-1]

split(vis=ms_dataset, outputvis=output_dataset, datacolumn=datacolumn, spw=spw)
