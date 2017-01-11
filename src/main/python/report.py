import logging
from models.antenna_status import AntennaStatus


class Report:
    def __init__(self, antennas):
        self.__antennas = antennas

    def generate_report(self, scan_ids):
        logging.info("AntennaId, Polarisation, ScanId, R_Status, CP_Status")
        for ant in self.__antennas:
            for state in ant.get_states():
                if state.scan_id in scan_ids and (state.get_R_phase_status() == AntennaStatus.BAD or state.get_closure_phase_status() == AntennaStatus.BAD):
                    logging.info("   {0}\t   \t{1}\t   {2}\t   {3}\t     {4}".format(
                        ant.id, state.polarization, state.scan_id, state.get_R_phase_status(), state.get_closure_phase_status()))