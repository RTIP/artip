import sys
import json

polarizations = sys.argv[-6]
ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
key = sys.argv[-3]
scans = sys.argv[-2].split(",")
source_type = sys.argv[-1]

data = {}
data[key] = {}


def file_name():
    if source_type == "-":
        return '{0}/{1}.json'.format(output_path, key)
    return '{0}/{1}_{2}.json'.format(output_path, key, source_type)


for scan_no in scans:
    data[key][scan_no] = {}
    data[key][scan_no]["source_type"] = source_type
    data[key][scan_no]["polarizations"] = {}
    for pol in polarizations.split(","):
        summary = flagdata(vis=ms_dataset, mode='summary', scan=scan_no, correlation=pol)
        data[key][scan_no]["polarizations"][pol] = summary

json_data = json.dumps(data)
with open(file_name(), 'w') as outfile:
    json.dump(data, outfile)
