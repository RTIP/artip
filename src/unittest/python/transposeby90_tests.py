import unittest
from transpose_by_90 import *

class TransposeBy90Test(unittest.TestCase):

    def test_data_near_zero(self):
        data= [-30,-20,-10,0,10,20,30]
        transposed_data = transpose_by_90(data)
        self.assertEqual(transposed_data, [60,70,80,90,100,110,120])

    def test_data_near_180(self):
        data= [-160,-170,-175,180,170,160]
        transposed_data = transpose_by_90(data)
        self.assertEqual(transposed_data, [-70, -80, -85, -90, -100, -110])

    def test_positive_data(self):
        data= [-179, 180, 120, 90, 60, 30]
        transposed_data = transpose_by_90(data)
        self.assertEqual(transposed_data, [-89,-90,-150, -180, 150, 120])

    def test_is_dispersed_positive_data(self):
        data= [10,20,30,40,50,90]
        self.assertEqual(is_dispersed(data), False)

    def test_is_good_for_positive_data(self):
        data= [10,20,30,40,50,90,100]
        self.assertEqual(is_good(data), True)

    def test_is_good_for_positive_data_falsy(self):
        data= [10,20,30,40,50,90,120]
        self.assertEqual(is_good(data), False)

    def test_is_good_for_positive_data_falsy(self):
        data= [-179, 180, 120, 90]
        self.assertEqual(is_good(data), True)

    def test_is_good_for_bad_data_should_fail(self):
        data= [0, -90, -179]
        self.assertEqual(is_good(data), False)

    def test_is_good(self):
        data= [-1, 90]
        self.assertEqual(is_good(data), True)
