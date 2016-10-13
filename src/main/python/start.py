import casac
import numpy as np
import scipy.stats as stats
import pylab as pl
import matplotlib.pyplot as plt

def plot_pdf(data, antenna):
    fit = stats.norm.pdf(data, np.mean(data), np.std(data))
    pl.plot(data,fit,'-o')
    pl.hist(data,normed=True)
    pl.ion()
    pl.show()
    pl.savefig('pdf%s.png' % antenna)
    plt.clf()

def plot_percentiles(data, antenna):
    percentiles = range(0,100,5)
    plt.plot(percentiles, np.percentile(data,percentiles), c='green')
    plt.ion()
    plt.show()
    plt.savefig('percentile_%s.png' %antenna)


def toDegree(angleInRadians):
    angleInDegree = int(angleInRadians * (180 / 3.14))
    if angleInDegree<0 :
        return 360-abs(angleInDegree)
    else:
        return angleInDegree


def main(args=None):
    ms = casac.casac.ms ()
    ms.open('/Users/dollyg/Projects/IUCAA/output/may14.ms')
    ms.selectinit(reset=True)
    antennas = filter(lambda antenna: antenna!=2, range(3, 29, 1))
    print antennas
    for antenna1 in antennas:
        ms.selectinit(reset=True)
        ms.selectpolarization('RR')
        ms.selectchannel(start=100)
        ms.select({'scan_number': 1, 'antenna1': 2, 'antenna2': antenna1})
        phase_data = ms.getdata(['phase'])['phase'][0][0]
        phase_data_in_degrees = map(lambda pd: toDegree(pd), phase_data)
        plot_pdf(phase_data_in_degrees, antenna1)
        print antenna1, stats.variation(phase_data_in_degrees)
        print phase_data_in_degrees


if __name__ == "__main__":
    main()