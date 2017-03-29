from unittest import TestCase
import numpy
from closure_phase_util import ClosurePhaseUtil


class ClosurePhaseUtilTest(TestCase):
    def test_should_closure_phase_of_given_triad_antennas_as_0(self):
        antenna_1, antenna_2, antenna_3 = 0, 1, 2
        antenna_1_list = numpy.array([0, 0, 1])
        antenna_2_list = numpy.array([1, 2, 2])
        baseline_0_1_phase = 2.0
        baseline_0_2_phase = 3.2
        baseline_1_2_phase = 1.2
        phases = numpy.array([[[[baseline_0_1_phase], [baseline_0_2_phase], [baseline_1_2_phase]]]])
        closure_phase_util = ClosurePhaseUtil()

        expected_value = (baseline_0_1_phase + baseline_1_2_phase) - baseline_0_2_phase
        self.assertEqual(closure_phase_util.closurePhTriads((antenna_1, antenna_2, antenna_3),phases, antenna_1_list,antenna_2_list), expected_value)

    def test_should_closure_phase_of_given_triad_antennas_as_minus_1(self):
        antenna_1, antenna_2, antenna_3 = 0, 1, 2
        antenna_1_list = numpy.array([0, 0, 1])
        antenna_2_list = numpy.array([1, 2, 2])
        baseline_0_1_phase = 2.0
        baseline_0_2_phase = 4.2
        baseline_1_2_phase = 1.2
        phases = numpy.array([[[[baseline_0_1_phase], [baseline_0_2_phase], [baseline_1_2_phase]]]])
        closure_phase_util = ClosurePhaseUtil()

        expected_value = (baseline_0_1_phase + baseline_1_2_phase) - baseline_0_2_phase
        self.assertEqual(closure_phase_util.closurePhTriads((antenna_1, antenna_2, antenna_3),phases, antenna_1_list,antenna_2_list), expected_value)

    def test_should_closure_phase_of_given_triad_antennas_as_2(self):
        antenna_1, antenna_2, antenna_3 = 0, 1, 2
        antenna_1_list = numpy.array([0, 0, 1])
        antenna_2_list = numpy.array([1, 2, 2])
        baseline_0_1_phase = 2.0
        baseline_0_2_phase = 1.2
        baseline_1_2_phase = 1.2
        phases = numpy.array([[[[baseline_0_1_phase], [baseline_0_2_phase], [baseline_1_2_phase]]]])
        closure_phase_util = ClosurePhaseUtil()

        expected_value = (baseline_0_1_phase + baseline_1_2_phase) - baseline_0_2_phase
        self.assertEqual(closure_phase_util.closurePhTriads((antenna_1, antenna_2, antenna_3),phases, antenna_1_list,antenna_2_list), expected_value)