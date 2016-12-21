import numpy
from debugging_config import *

def calculate_median(list):
    return numpy.median(numpy.array(list))

def minus(list1, list2):
    return filter(lambda elm: elm not in list2, list1)


class Debugger:
    def filter_matrix(self,amp_matrix):
        for antenna_id in DEBUG_FLAG_ELEMENTS['antennas']:
            for baseline in amp_matrix.keys():
                if baseline.contains(antenna_id):
                    del amp_matrix[baseline]

        for flagged_baseline in DEBUG_FLAG_ELEMENTS['baselines']:
            for baseline in amp_matrix.keys():
                if baseline.antenna1 == flagged_baseline[0] and baseline.antenna2 == flagged_baseline[1]:
                    del amp_matrix[baseline]

        for time_index in DEBUG_FLAG_ELEMENTS['time']:
            for baseline in amp_matrix.keys():
                amp_matrix[baseline][time_index] = -1
                amp_matrix[baseline] = filter(lambda x: x != -1, amp_matrix[baseline])
