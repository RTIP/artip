import unittest
from angular_dispersion import calculate_angular_dispersion
from angular_dispersion import to_radians
from angular_dispersion import is_dispersed

class AngularDispersionTest(unittest.TestCase):

    def test_angular_dispersion_for_good_data_should_be_near_1(self):
        data= to_radians([-30,-20,-10,0,10,20,30,40])

        r = calculate_angular_dispersion(data)
        self.assertAlmostEqual(r, 0.9218950889, 10)

    def test_angular_dispersion_for_bad_data_should_be_near_0(self):
        data= to_radians([-170,-150,-120,-100,-90,-30,-20,-10,0,10,20,30,40,90,120,180])
        r = calculate_angular_dispersion(data)
        self.assertAlmostEqual(r, 0.2171490554, 10)

    def test_is_dispersed_should_return_false_for_good_data(self):
        data= to_radians([-30,-20,-10,0,10,20,30,40])
        self.assertFalse(is_dispersed(data))

    def test_is_dispersed_should_return_true_for_bad_data(self):
        data= to_radians([-170,-150,-120,-100,-90,-30,-20,-10,0,10,20,30,40,90,120,180])
        self.assertTrue(is_dispersed(data))