"""
Access this script with below command:
python generate_graph.py <Path of json_store in output dir>
Example: python generate_graph.py "/Users/sarangk/Project/IUCAA/artip/output/may14/json_store"
"""

import json
import SimpleHTTPServer
import SocketServer
import sys

graph_data = {}


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


def build_json(input_file):
    with open(input_file) as data_file:
        data = json.load(data_file)
        stage = data.keys()[0]
        for scan, scan_val in data[stage].iteritems():
            if scan not in graph_data:
                graph_data[scan] = {}
                graph_data[scan]["polarizations"] = {}
            for pol, pol_val in scan_val["polarizations"].iteritems():
                if pol not in graph_data[scan]["polarizations"]:
                    graph_data[scan]["polarizations"][pol] = {}
                    graph_data[scan]["polarizations"][pol]["antennas"] = []
                for antenna, antenna_val in pol_val["antenna"].iteritems():
                    antenna_row = get_antenna_row(graph_data[scan]["polarizations"][pol]["antennas"], antenna)
                    if antenna_row:
                        set_percentage_value_to_stage(antenna_val, antenna_row, stage)
                        set_source_type(scan_val, scan)
                    else:
                        initialize_antenna_row(antenna, antenna_row)
                        set_percentage_value_to_stage(antenna_val, antenna_row, stage)
                        graph_data[scan]["polarizations"][pol]["antennas"].append(antenna_row)
                        set_source_type(scan_val, scan)
    return graph_data


def initialize_antenna_row(antenna, antenna_row):
    antenna_row["antenna"] = antenna
    antenna_row["prev_flagged"] = 0


def set_percentage_value_to_stage(antenna_val, antenna_row, key):
    antenna_row[key] = calculate_percentage((antenna_val['flagged'] - antenna_row['prev_flagged']),
                                            antenna_val['total'])
    antenna_row["prev_flagged"] = antenna_val["flagged"]


def set_source_type(scan_val, scan):
    if scan_val["source_type"] != "All":
        graph_data[scan]["source_type"] = scan_val["source_type"]


def iterate_over_json_store():
    json_store_path = sys.argv[1]
    print "Parsing flag summaries"
    build_json("{0}/known_flags_All.json".format(json_store_path))
    build_json("{0}/rang_closure_flux_calibrator.json".format(json_store_path))
    build_json("{0}/detailed_flagging_flux_calibrator.json".format(json_store_path))
    build_json("{0}/rang_closure_phase_calibrator.json".format(json_store_path))
    build_json("{0}/detailed_flagging_phase_calibrator.json".format(json_store_path))


def run_server():
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "Access graphs at port ", PORT
    httpd.serve_forever()


if __name__ == "__main__":
    iterate_over_json_store()
    with open('graph.json', 'w') as outfile:
        json.dump(graph_data, outfile)
    run_server()
