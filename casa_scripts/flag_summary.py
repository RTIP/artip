import sys
from tinydb import TinyDB, Query

script_parameters_start_index = sys.argv.index('-c') + 2
parameters = sys.argv[script_parameters_start_index:]

polarizations = parameters[0].split(",")
ms_dataset = parameters[1]
output_path = parameters[2]
flagging_type = parameters[3]
scans = parameters[4].split(",")
source_type = parameters[5]

db_file = '{0}/flag_summary.json'.format(output_path)
dataset_name = ms_dataset.split("/")[-1]

db = TinyDB(db_file)
dataset = Query()

rows = []
for scan in scans:
    for pol in polarizations:
        summary = flagdata(vis=ms_dataset, mode='summary', scan=scan, correlation=pol)
        antenna = summary["antenna"]
        rows.append(
            {'dataset': dataset_name, 'source_type': source_type, "scan": scan, "pol": pol, flagging_type: antenna})

db.insert_multiple(rows)
db.close()
