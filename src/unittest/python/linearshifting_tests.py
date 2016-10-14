import unittest
from linearshifting import shift_linear


class LinearShiftingTest(unittest.TestCase):

    def test_positive_phase_data(self):
        data = [0,10,20,30,40,70,90,180]
        shiftedData = shift_linear(data)
        self.assertEqual(shiftedData, data)

    def test_negative_phase_data(self):
        data = [-10,-20,-30,-40,-70,-90,-170]
        shiftedData = shift_linear(data)
        self.assertEqual(shiftedData, data)

    def test_phase_data_near_zero(self):
        data = [-40,-20,-10,0,10,20,40]
        shiftedData = shift_linear(data)
        self.assertEqual(shiftedData, [0,20,30,40,50,60,80])

    def test_phase_data_near_180(self):
        data = [-160,-170,180,170,160]
        shiftedData = shift_linear(data)
        self.assertEqual(shiftedData, [0,10,20,30,40])

    def test_phase_data_(self):
        data = [-160,-170,180,170,160]
        shiftedData = shift_linear(data)
        self.assertEqual(shiftedData, [0,10,20,30,40])