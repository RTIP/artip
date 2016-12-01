import matplotlib.pyplot as pyplot
import numpy
import pylab
import scipy.stats as stats


class Plotter:
    @staticmethod
    def plot_pdf(data, antenna):
        fit = stats.norm.pdf(data, numpy.mean(data), numpy.std(data))
        pylab.plot(data, fit, '-o')
        pylab.hist(data, normed=True)
        pylab.ion()
        pylab.show()
        pylab.savefig('pdf%s.png' % antenna)
        pyplot.clf()

    @staticmethod
    def plot_percentiles(data, antenna):
        percentiles = range(0, 100, 5)
        pyplot.plot(percentiles, numpy.percentile(data, percentiles), c='green')
        pyplot.ion()
        pyplot.show()
        pyplot.savefig('percentile_%s.png' % antenna)
