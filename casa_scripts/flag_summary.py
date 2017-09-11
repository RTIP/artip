import sys
import json

ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
key = sys.argv[-3]
scans = sys.argv[-2].split(",")
source_type = sys.argv[-1]

data = {}
data[key] = {}

for scan_no in scans:
    summary = flagdata(vis=ms_dataset, mode='summary', scan=scan_no)
    data[key][scan_no] = summary
    data[key][scan_no]["source_type"] = source_type

json_data = json.dumps(data)
with open('{0}/{1}_{2}.json'.format(output_path, key, source_type), 'w') as outfile:
    json.dump(data, outfile)
