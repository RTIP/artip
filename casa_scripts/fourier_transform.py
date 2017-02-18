import sys

ms_dataset = sys.argv[-3]
field_name = sys.argv[-2]
model_name = sys.argv[-1]

ft(vis=ms_dataset, field=field_name, model=model_name)
