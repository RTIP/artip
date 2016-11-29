from unittest import TestCase
from phase_set import PhaseSet
from config import FLUX_CAL_CONFIG
import math


class PhaseSetTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.r_threshold = FLUX_CAL_CONFIG['r_threshold']

    def test_is_dispersed_should_return_false_for_dispersion_of_less_than_200_degrees_for_flux_calibrator(self):
        phase_data_in_radian = self.degree_to_radian(
            [41, 50, 50, 29, 13, 10, 14, 12, 22, 47, 31, 34, 43, 40, 40, 42, 15, 13, 41, 24, 13, 22, 28, 47, 37])
        phase_set = PhaseSet(phase_data_in_radian)
        self.assertFalse(phase_set.is_dispersed(self.r_threshold))

    def test_is_dispersed_should_return_true_for_dispersion_more_than_270_degrees(self):
        phase_data_in_radian = self.degree_to_radian(
            [19, 28, 8, 200, 20, 190, 92, 15, 145, 118, 211, 266, 189, 89, 56, 52, 178, 162, 149, 169, 219, 26, 270,
             235, 67])
        phase_set = PhaseSet(phase_data_in_radian)
        self.assertTrue(phase_set.is_dispersed(self.r_threshold))

    def test_is_dispersed_should_return_false_for_data_having_outliers(self):
        phase_data = [41, 50, 50, 29, 13, 10, 14, 12, 22, 47, 34, 13, 41, 24, 13, 22, 28, 47, 37]
        outliers = [290, 270, 280, 359, 320]
        phase_data_in_radian = self.degree_to_radian(phase_data + outliers)
        phase_set = PhaseSet(phase_data_in_radian)
        self.assertFalse(phase_set.is_dispersed(self.r_threshold))

    def degree_to_radian(self, phase_set_in_degree):
        return map(lambda phase: math.radians(phase), phase_set_in_degree)
