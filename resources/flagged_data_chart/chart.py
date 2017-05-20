import pygal
import casac
import sys
import yaml
import numpy
import collections
from math import ceil
from tinydb import TinyDB, Query
from operator import itemgetter
from os import path
db = TinyDB('tiny_db.json')
ms = casac.casac.ms()
ms.open(sys.argv[1])
plot_identifier = 'plot'
dataset_name = path.splitext(path.basename(sys.argv[1]))[0]

def load_inputs():
		input_file = open('./chart_config.yml')
		inputs = yaml.load(input_file)
		input_file.close()
		return inputs
inputs = load_inputs()

def antennaids():
	first_scan_id = ms.metadata().scannumbers()[0]
	return ms.metadata().antennasforscan(first_scan_id).tolist()

antennaids = antennaids()
antennaids.sort()

def create_baselines(antenna1_list,antenna2_list,flags):
	baselines = {}
	for antenna1 in antennaids:
		for antenna2 in antennaids:
			if antenna1 < antenna2:
				primary_antenna = antenna1
				secondary_antenna = antenna2
			else:
				primary_antenna = antenna2
				secondary_antenna = antenna1
			if primary_antenna == secondary_antenna: continue

			baseline_indexes = numpy.logical_and(antenna1_list == primary_antenna,antenna2_list == secondary_antenna).nonzero()[0]
			baseline_flags_data = numpy.array([])
			for index in baseline_indexes:
				baseline_flags_data = numpy.append(baseline_flags_data, flags[index])
			baselines[(primary_antenna, secondary_antenna)] = baseline_flags_data
	return baselines            

def get_flags_for_all_baselines():
	ms.selectinit(reset=True)
	ms.msselect({"spw": inputs['spw']})
	ms.selectpolarization(inputs['polarization'])
	ms.selectchannel(**{'start': inputs['channel'],'width':inputs['channel_width']})
	# ms.select({'scan_number': inputs['scan_id']})
	data = ms.getdata(["antenna1", "antenna2",'flag'])
	antenna1_list = data['antenna1']
	antenna2_list = data['antenna2']
	flags = data['flag'][0][0]
	return create_baselines(antenna1_list,antenna2_list,flags)

if sys.argv[2] != plot_identifier:
	baseline_flags_data=get_flags_for_all_baselines()

def contains(baseline,antenna_id):
	return baseline[0]==antenna_id or baseline[1]==antenna_id


def filter_by_antenna(antenna_id):
	return dict((baseline, flag_data) for baseline, flag_data in baseline_flags_data.iteritems() if contains(baseline,antenna_id))

def calculate_baseline_flag_percentage():
	baseline_falg_perc = {}
	for (baseline, flags) in baseline_flags_data.items():
		total = flags.shape[0]
		flagged = collections.Counter(flags)[1.0]
		baseline_falg_perc["{0}_{1}".format(baseline[0],baseline[1])] = ceil((float(flagged)/total) * 100)
	return	baseline_falg_perc

def calculate_antennas_flag_percentage():
	antenna_falg_perc = {}
	for antenna_id in antennaids:
		antenna_flags=numpy.array(filter_by_antenna(antenna_id).values()).flatten()
		total = antenna_flags.shape[0]
		flagged = collections.Counter(antenna_flags)[1.0]
		antenna_falg_perc[antenna_id] = ceil((float(flagged)/total) * 100)
	return antenna_falg_perc

def plot_antenna_percentage(plot_name):
	User = Query()
	dataset_data=db.search(User.dataset_name.matches(dataset_name))
	line_chart = pygal.Bar()
	line_chart.title = "Flagged Antenna data percentage on {0}.ms \n{1}".format(dataset_name,inputs)
	line_chart.x_labels = map(str, antennaids)
	for data in dataset_data:
		flagged_ant_perc = map(lambda x: x[1],sorted(data['antennas_flag_perc'].items(), key=lambda ant: int(ant[0])))
		line_chart.add(data['stage'], flagged_ant_perc)		
	line_chart.render_to_file(plot_name)


def plot_baseline_percentage(plot_name):
	User = Query()
	dataset_data=db.search(User.dataset_name.matches(dataset_name))
	line_chart = pygal.StackedLine(fill=True)
	line_chart.title = "Flagged Baseline data percentage on {0}".format(dataset_name)
	line_chart.x_labels = map(str, dataset_data[0]['baseline_flag_perc'].keys())
	for data in dataset_data:
		line_chart.add(data['stage'], data['baseline_flag_perc'].values())		
	line_chart.render_to_file(plot_name)

if sys.argv[2] == plot_identifier:
	plot_antenna_percentage("{0}_antenna_per.svg".format(dataset_name))
	plot_baseline_percentage("{0}_baseline_per.svg".format(dataset_name))
else:
	calculate_baseline_flag_percentage()
	db.insert({'dataset_name': dataset_name,'stage':sys.argv[2],
		'antennas_flag_perc':calculate_antennas_flag_percentage(),
		'baseline_flag_perc':calculate_baseline_flag_percentage()})