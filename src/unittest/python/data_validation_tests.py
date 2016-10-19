import unittest
from data_validation import validate

class DataValidationTests(unittest.TestCase):

    def test_validate_for_positive_data(self):
        data= [10,20,30,40,50,90,100]
        self.assertEqual(validate(data), True)

    def test_invalidate_for_positive_dispersed_data(self):
        data= [10,20,30,40,50,90,120]
        self.assertEqual(validate(data), False)

    def test_invalidate_negative_dispersed_data(self):
        data= [0, -90, -179]
        self.assertEqual(validate(data), False)

    def test_validate_for_circular_data_near_0(self):
        data= [-1, 90]
        self.assertEqual(validate(data), True)

    def test_validate_for_circular_data_near_180(self):
        data= [-179, 180, 120, 90]
        self.assertEqual(validate(data), True)
