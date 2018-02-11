import numpy

class ClosurePhaseUtil:
    def closurePhTriads(self, triad, data):
        signed_phase_triplet = self._triadRows(data.antenna1, data.antenna2, triad)
        closure_phase = self._rewrap(self._calculate_clousure_phase(signed_phase_triplet, data))
        # NOTE: filtering out flagged closure_phases
        # By doing this we will get correct statistics from percentileofscore in closure analyser
        return numpy.array(filter(lambda phase: not numpy.isnan(phase), closure_phase))

    def _calculate_clousure_phase(self, signed_phase_triplet, data):
        (phase1_index, phase2_index, phase3_index), (sign1, sign2, sign3) = signed_phase_triplet
        baseline1_data = numpy.array(data.mask_baseline_data(phase1_index))
        baseline2_data = numpy.array(data.mask_baseline_data(phase2_index))
        baseline3_data = numpy.array(data.mask_baseline_data(phase3_index))

        return baseline1_data * sign1 + baseline2_data * sign2 + baseline3_data * sign3

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
