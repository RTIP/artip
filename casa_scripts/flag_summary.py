import sys
from tinydb import TinyDB, Query

polarizations = sys.argv[-6].split(",")
ms_dataset = sys.argv[-5]
output_path = sys.argv[-4]
flagging_type = sys.argv[-3]
scans = sys.argv[-2].split(",")
source_type = sys.argv[-1]

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
