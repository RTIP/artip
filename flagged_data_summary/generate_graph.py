"""
Access this script with below command:
python generate_graph.py <Path of json_store in output dir>
Example: python generate_graph.py "/Users/sarangk/Project/IUCAA/artip/output/may14/json_store"
"""

import json
import SimpleHTTPServer
import SocketServer
import sys

FLAGGING_SEQUENCE = ["known_flags", "rang_closure", "detailed_flagging", "tfcrop", "rflag"]


def get_antenna_row(scan_data, antenna):
    for row in scan_data:
        if "antenna" in row:
            if row["antenna"] == antenna:
                return row
    return {}


def calculate_percentage(favourable, total):
    try:
        percentage = (float(favourable) / float(total)) * 100
    except ZeroDivisionError:
        percentage = 0
    return percentage


def build_json():
    dashboard = []

    input_file = "{0}/flag_summary.json".format(sys.argv[1])
    with open(input_file) as data_file:
        datasets = json.load(data_file)
        for dataset_name, dataset in datasets.iteritems():
            graph = {}
            graph["dataset"] = dataset_name
            for scan, scan_val in dataset.iteritems():
                if scan not in graph:
                    graph[scan] = {}
                    graph[scan]["source_type"] = scan_val["source_type"]
                    if "polarization" not in graph[scan]:
                        graph[scan]["polarization"] = {}
                for pol, pol_value in scan_val["polarization"].iteritems():
                    if pol not in graph[scan]["polarization"]:
                        graph[scan]["polarization"][pol] = {}

                    for flag_type in FLAGGING_SEQUENCE:
                        if flag_type in scan_val["polarization"][pol]:
                            flag_summary = scan_val["polarization"][pol][flag_type]
                        else:
                            continue
                        if "antenna" not in graph[scan]["polarization"][pol]:
                            graph[scan]["polarization"][pol]["antenna"] = []
                        for antenna, antenna_val in flag_summary["antenna"].iteritems():
                            antenna_row = get_antenna_row(graph[scan]["polarization"][pol]["antenna"], antenna)
                            if antenna_row:
                                set_percentage_value_to_stage(antenna_val, antenna_row, flag_type)
                                set_source_type(scan_val, scan, graph)
                            else:
                                initialize_antenna_row(antenna, antenna_row)
                                set_percentage_value_to_stage(antenna_val, antenna_row, flag_type)
                                graph[scan]["polarization"][pol]["antenna"].append(antenna_row)
                                set_source_type(scan_val, scan, graph)
            dashboard.append(graph)
    return dashboard


def initialize_antenna_row(antenna, antenna_row):
    antenna_row["antenna"] = antenna
    antenna_row["prev_flagged"] = 0


def set_percentage_value_to_stage(antenna_val, antenna_row, key):
    antenna_row[key] = calculate_percentage((antenna_val['flagged'] - antenna_row['prev_flagged']),
                                            antenna_val['total'])
    antenna_row["prev_flagged"] = antenna_val["flagged"]


def set_source_type(scan_val, scan, graph):
    if scan_val["source_type"] != "All":
        graph[scan]["source_type"] = scan_val["source_type"]


def run_server():
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "Access graphs at port ", PORT
    httpd.serve_forever()


if __name__ == "__main__":
    dashboard = build_json()
    with open('graph.json', 'w') as outfile:
        json.dump(dashboard, outfile)
    run_server()
