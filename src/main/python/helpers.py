import numpy
import math
import os

from configs.pipeline_config import FLAGGED_ELEMENTS


def calculate_median(list):
    return numpy.nanmedian(numpy.array(list))


def minus(list1, list2):
    return filter(lambda elm: elm not in list2, list1)


def nCr(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n - r)


def is_last_element(ele, elements):
    return ele == elements[len(elements) - 1]


def delete_indexes(array, indexes):
    result = []
    for index, time_index in enumerate(indexes):
        result = numpy.delete(array, time_index, 0) if index == 0 else numpy.delete(result, time_index - 1, 0)
    return result


def is_nan(array):
    return all(numpy.isnan(amp) for amp in numpy.array(array).flatten())


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.abspath(directory)


class Debugger:
    def __init__(self, measurement_set):
        self._measurement_set = measurement_set

    def flag_antennas(self, polarization, scan_ids):
        self._measurement_set.flag_antennas(polarization, scan_ids, FLAGGED_ELEMENTS['antennas'])
