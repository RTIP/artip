import matplotlib.pyplot as pyplot
from matplotlib.colors import from_levels_and_colors
import numpy
import pylab
import os


class Plotter:
    @staticmethod
    def plot_pdf(data, triplet, threshold, name_prefix):
        ar = numpy.arange(0, len(data), 1)
        pyplot.xlabel("Timerange")
        pyplot.ylabel("Closure Phase (Absolute)")
        colors = ['blue', 'red']
        levels = [0, 1]
        cmap, norm = from_levels_and_colors(levels=levels, colors=colors, extend='max')
        phases_in_degree = numpy.array(numpy.absolute(data)) * 180 / numpy.pi
        good_or_bad = numpy.where(phases_in_degree < threshold, 0, 1)

        pyplot.scatter(ar, numpy.zeros_like(ar) + phases_in_degree, c=good_or_bad, cmap=cmap, norm=norm,
                       edgecolor='none')
        pylab.ion()
        pylab.show()
        path = os.path.abspath("plots")
        pylab.savefig(path + '/Triplet-{0}_{1}.png'.format(name_prefix, triplet))
        pyplot.clf()

    @staticmethod
    def plot_percentiles(data, antenna):
        percentiles = range(0, 100, 5)
        pyplot.plot(percentiles, numpy.percentile(data, percentiles), c='green')
        pyplot.ion()
        pyplot.show()
        pyplot.savefig('percentile_%s.png' % antenna)
