import numpy
import math

def calculate_angular_dispersion(phases):
    sinx = map(lambda phase: math.sin(phase), phases)
    cosx = map(lambda phase: math.cos(phase), phases)
    avg_sin = numpy.mean(sinx)
    avg_cos = numpy.mean(cosx)

    r = math.sqrt(math.pow(avg_sin, 2) + math.pow(avg_cos, 2))
    return r

def is_dispersed(data):
    r = calculate_angular_dispersion(data)
    return r<0.5

def to_radians(data):
    return map(lambda x: math.radians(x), data)