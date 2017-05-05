import sys

ms_dataset = sys.argv[-3]
spw = sys.argv[-4]
field = sys.argv[-2]
model_path = sys.argv[-1]
setjy(vis=ms_dataset, field=field, spw=spw, modimage=model_path, usescratch=True)