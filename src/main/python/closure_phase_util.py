import numpy


class ClosurePhaseUtil:
    def closurePhTriads(self, triad, phase_data, antenna1_list, antenna2_list):
        signed_phase_triplet = self._triadRows(antenna1_list, antenna2_list, triad)
        closure_phase = self._rewrap(self._calculate_clousure_phase(phase_data, signed_phase_triplet))
        return closure_phase

    def _calculate_clousure_phase(self, phase_data, signed_phase_triplet):
        (phase1_index, phase2_index, phase3_index), (sign1, sign2, sign3) = signed_phase_triplet
        return phase_data[:, :, phase1_index, :] * sign1 + \
               phase_data[:, :, phase2_index, :] * sign2 + \
               phase_data[:, :, phase3_index, :] * sign3

    def _rewrap(self, phase):
        return numpy.arctan2(numpy.sin(phase), numpy.cos(phase))

    def _get_phase_index_with_sign_for(self, antenna1, antenna2, i_index, j_index):
        r1 = numpy.logical_and(antenna1 == i_index, antenna2 == j_index).nonzero()[0]
        if r1.shape[0]:
            return r1[0], +1.0
        else:
            try:
                return numpy.logical_and(antenna1 == j_index, antenna2 == i_index).nonzero()[0][0], -1.0
            except IndexError:
                print 'antenna1,antenna2', antenna1, antenna2

    def _triadRows(self, antenna1_combinations, antenna2_combinations, triad):
        antenna1, antenna2, antenna3 = triad
        p1, s1 = self._get_phase_index_with_sign_for(antenna1_combinations, antenna2_combinations, antenna1, antenna2)
        p2, s2 = self._get_phase_index_with_sign_for(antenna1_combinations, antenna2_combinations, antenna2, antenna3)
        p3, s3 = self._get_phase_index_with_sign_for(antenna1_combinations, antenna2_combinations, antenna3, antenna1)
        return ((p1, p2, p3),
                (s1, s2, s3))
