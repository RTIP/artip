import unittest
from normalization import normalize

class NormalizationTest(unittest.TestCase):

    def test_normalize_data_near_zero(self):
        data= [-30,-20,-10,0,10,20,30]
        normalized_data = normalize(data)
        self.assertEqual(normalized_data, [60,70,80,90,100,110,120])

    def test_normalize_data_near_180_degree(self):
        data= [-160,-170,-175,180,170,160]
        normalized_data = normalize(data)
        self.assertEqual(normalized_data, [-70, -80, -85, -90, -100, -110])

    def test_normalize_all_positive_data(self):
        data= [180, 120, 90, 60, 30]
        normalized_data = normalize(data)
        self.assertEqual(normalized_data, data)

    def test_normalized_all_negative_data(self):
        data= [-180, -120, -90, -60, -30]
        normalized_data = normalize(data)
        self.assertEqual(normalized_data, data)