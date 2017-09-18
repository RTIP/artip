"""
Access this script with below command:
python generate_graph.py <Path of json_store in output dir>
Example: python generate_graph.py "/Users/sarangk/Project/IUCAA/artip/output/may14/json_store"
"""

import json
import SimpleHTTPServer
import SocketServer
import sys
from tinydb import TinyDB

FLAGGING_SEQUENCE = ["known_flags", "rang_closure", "detailed_flagging", "tfcrop", "rflag"]


def get_antenna_row(antennas, antenna_id):
    if antennas:
        filtered_antennas = filter(lambda ant: ant['antenna'] == antenna_id, antennas)
        if len(filtered_antennas) > 0:
            return filtered_antennas[0]
    return {}


def calculate_percentage(favourable, total):
    try:
        percentage = (float(favourable) / float(total)) * 100
    except ZeroDivisionError:
        percentage = 0
    return percentage


def set_percentage_value_to_stage(antenna_val, antenna_row, key):
    antenna_row[key] = calculate_percentage((antenna_val['flagged'] - antenna_row['prev_flagged']),
                                            antenna_val['total'])
    antenna_row["prev_flagged"] = antenna_val["flagged"]


def build_node(node_name, parent_node, default_value):
    if not parent_node.get(node_name):
        parent_node[node_name] = default_value
    return parent_node[node_name]


def add_to_list(list, element):
    if element not in list:
        list.append(element)


def build_json():
    db_file = '{0}/json_store/flag_summary.json'.format(sys.argv[1])
    db = TinyDB(db_file)
    graph = {}
    flags = db.all()
    for row in flags:
        dataset = build_node(row['dataset'], graph, {})
        scan_node = build_node(row['scan'], dataset, {})
        source_type_node = build_node('source_type', scan_node, [])
        add_to_list(source_type_node, row['source_type'])
        pol_node = build_node('polarization', scan_node, {})
        antennas_per_pol = build_node(row['pol'], pol_node, [])
        for flagging_type in FLAGGING_SEQUENCE:
            if not row.get(flagging_type):
                continue
            for antenna_id, antenna_val in row[flagging_type].iteritems():
                ant_node = get_antenna_row(antennas_per_pol, antenna_id)
                if ant_node:
                    set_percentage_value_to_stage(antenna_val, ant_node, flagging_type)
                else:
                    initialize_antenna_row(antenna_id, ant_node)
                    set_percentage_value_to_stage(antenna_val, ant_node, flagging_type)
                    antennas_per_pol.append(ant_node)
    return graph


def initialize_antenna_row(antenna, antenna_row):
    antenna_row["antenna"] = antenna
    antenna_row["prev_flagged"] = 0


def run_server():
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "Access graphs at port ", PORT
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "Exiting server..."
        httpd.server_close()


if __name__ == "__main__":
    dashboard = build_json()
    with open('graph.json', 'w') as outfile:
        json.dump(dashboard, outfile)
    run_server()
