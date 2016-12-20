import numpy

def calculate_median(list):
    return numpy.median(numpy.array(list))

def minus(list1, list2):
    return filter(lambda elm: elm not in list2, list1)