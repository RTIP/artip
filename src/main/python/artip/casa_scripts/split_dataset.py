script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

ms_dataset = parameters[0]
output_dataset = parameters[1]
field = parameters[2]
datacolumn = parameters[3]
width = [int(v) for v in parameters[4].split(',')]
spw = "" if parameters[5] == 'all' else parameters[5]

split(vis=ms_dataset, outputvis=output_dataset, field=field, spw=spw, width=width, datacolumn=datacolumn)
