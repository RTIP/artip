import sys
import json

polarizations = sys.argv[-6]
ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
flagging_type = sys.argv[-3]
scans = sys.argv[-2].split(",")
source_type = sys.argv[-1]

json_file = '{0}/flag_summary.json'.format(output_path)
dataset_name = ms_dataset.split("/")[-1]

datasets = {}


def create_or_load_file():
    global datasets
    try:
        with open(json_file) as data_file:
            datasets = json.load(data_file)
    except IOError:
        open(json_file, "w+")


create_or_load_file()


def create_key_or_get_value(data, key):
    if key not in data:
        data[key] = {}
    return data[key]


data = {}
data[dataset_name] = {}
if dataset_name in datasets.keys():
    data[dataset_name] = datasets[dataset_name]
dataset = data[dataset_name]
for scan_no in scans:
    scan_data = create_key_or_get_value(dataset, scan_no)
    scan_data["source_type"] = source_type
    polarization_data = create_key_or_get_value(scan_data, "polarization")
    for pol in polarizations.split(","):
        summary = flagdata(vis=ms_dataset, mode='summary', scan=scan_no, correlation=pol)
        pol_data = create_key_or_get_value(polarization_data, pol)
        if flagging_type not in pol_data:
            pol_data[flagging_type] = summary

datasets.update(data)

with open(json_file, 'w') as outfile:
    json.dump(datasets, outfile)
