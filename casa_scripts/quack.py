import sys

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

ms_dataset = parameters[0]

flagdata(vis=ms_dataset, mode='quack', quackinterval=48, quackmode='beg')
