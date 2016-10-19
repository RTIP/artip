from normalization import *

def is_dispersed(data):
    max_of_range = max(data)
    min_of_range = min(data)

    return max_of_range-min_of_range>100

def validate(data):
    if is_dispersed(data):
        data = normalize(data)

    return not is_dispersed(data)