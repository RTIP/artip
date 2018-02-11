import numpy
import math


class PhaseSet:
    INVALID_ANGULAR_DISPERSION = -1
    def __init__(self, phases):
        self._phases = phases

    def _avg_sine(self):
        sines = numpy.sin(self._phases)
        return numpy.nanmean(sines)

    def _avg_cosine(self):
        cosines = numpy.cos(self._phases)
        return numpy.nanmean(cosines)

    def calculate_angular_dispersion(self):
        if all(numpy.isnan(self._phases)): return PhaseSet.INVALID_ANGULAR_DISPERSION
        r = math.sqrt(math.pow(self._avg_sine(), 2) + math.pow(self._avg_cosine(), 2))
        return r

    def is_dispersed(self, r_threshold):
        r = self.calculate_angular_dispersion()
        return r < r_threshold
