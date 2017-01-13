import sys

ms_dataset = sys.argv[-3]
field = sys.argv[-2]
model_path = sys.argv[-1]
setjy(vis=ms_dataset, field=field, spw='0', modimage=model_path)