import operator
from artip.models.antenna_status import AntennaStatus

class RMatrix:
    def __init__(self, spw, polarization, scan_id):
        self.polarization = polarization
        self.spw = spw
        self.scan_id = scan_id
        self._r_matrix = {}

    def __repr__(self):
        return self.polarization + " " + str(self.scan_id) + str(self._r_matrix)

    def add(self, antenna1, antenna2, r_value):
        if antenna1 not in self._r_matrix.keys():
            self._r_matrix[antenna1] = {}
        self._r_matrix[antenna1].update({antenna2: r_value})

    def get_any_antennas(self, base_antenna, min_doubtful_antennas):
        sorted_r_matrix = sorted(self._r_matrix[base_antenna].items(), key=operator.itemgetter(1))
        new_doubtful_antenna_tuples = set(sorted_r_matrix[:min_doubtful_antennas])
        return map(lambda tuple: tuple[0], new_doubtful_antenna_tuples)

    def get_doubtful_antennas(self, base_antenna, r_threshold, min_doubtful_antennas):
        doubtful_antennas = set()
        if base_antenna not in self._r_matrix: return doubtful_antennas
        for antenna, r_value in self._r_matrix[base_antenna].iteritems():
            if r_value < r_threshold:
                doubtful_antennas.add(antenna)

        if len(doubtful_antennas) < min_doubtful_antennas:
            new_doubtful_antennas = self.get_any_antennas(base_antenna, min_doubtful_antennas)
            doubtful_antennas = doubtful_antennas.union(new_doubtful_antennas)

        for doubtful_antenna in doubtful_antennas:
            doubtful_antenna.update_state(self.polarization, self.scan_id, AntennaStatus.DOUBTFUL)

        return doubtful_antennas
