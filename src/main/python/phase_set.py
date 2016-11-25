import numpy
import math


class PhaseSet:
    def __init__(self, phases):
        self.__phases = phases

    def _avg_sine(self):
        sines = map(lambda phase: math.sin(phase), self.__phases)
        return numpy.mean(sines)

    def _avg_cosine(self):
        cosines = map(lambda phase: math.cos(phase), self.__phases)
        return numpy.mean(cosines)

    def _calculate_angular_dispersion(self):
        r = math.sqrt(math.pow(self._avg_sine(), 2) + math.pow(self._avg_cosine(), 2))
        return r

    def is_dispersed(self, r_threshold):
        r = self._calculate_angular_dispersion()
        return r < r_threshold