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
        key = data.keys()[0]
        for scan, val in data[key].iteritems():
            if scan not in graph_data:
                graph_data[scan] = {}
                graph_data[scan]["antennas"] = []
            for antenna, ajson in data[key][scan]["antenna"].iteritems():
                antenna_row = get_antenna_row(graph_data[scan]["antennas"], antenna)
                if antenna_row:
                    antenna_row[key] = calculate_percentage((ajson['flagged'] - antenna_row['prev_flagged']),
                                                            ajson['total'])
                    antenna_row["prev_flagged"] = ajson["flagged"]
                    graph_data[scan]["source_type"] = data[key][scan]["source_type"]
                else:
                    antenna_row["antenna"] = antenna
                    antenna_row["prev_flagged"] = 0
                    antenna_row[key] = calculate_percentage((ajson['flagged'] - antenna_row['prev_flagged']),
                                                            ajson['total'])
                    antenna_row["prev_flagged"] = ajson["flagged"]
                    graph_data[scan]["antennas"].append(antenna_row)
                    graph_data[scan]["source_type"] = data[key][scan]["source_type"]
    return graph_data


def iterate_over_json_store():
    json_store_path = sys.argv[1]
    print "Parsing flag summaries"
    build_json("{0}/quack_None.json".format(json_store_path))
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
