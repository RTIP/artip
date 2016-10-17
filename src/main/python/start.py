import casac
import numpy as np
import scipy.stats as stats
import pylab as pl
import matplotlib.pyplot as plt
from transpose_by_90 import *

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
    return  angleInDegree
    # if angleInDegree<0 :
    #     return 360-abs(angleInDegree)
    # else:
    #     return angleInDegree

def shiftToZero(data):
    degreeOfRotation = min(data)
    return map(lambda pd: pd+abs(degreeOfRotation), data)


def main(args=None):
    ms = casac.casac.ms ()
    ms.open('/Users/dollyg/Projects/IUCAA/output/may14.ms')
    ms.selectinit(reset=True)
    # antennas = filter(lambda antenna: antenna!=2, range(1, 29, 1))
    antennas = range(1, 29, 1)
    # antennas = [0]
    bad_antennas = []
    for antenna in antennas:
        ms.selectinit(reset=True)
        ms.selectpolarization('RR')
        ms.selectchannel(start=100)
        ms.select({'scan_number': 7, 'antenna1': 0, 'antenna2': antenna})
        phase_data = ms.getdata(['phase'])['phase'][0][0]
        phase_data_in_degrees = map(lambda pd: toDegree(pd), phase_data)

        if not is_good(phase_data_in_degrees):
            bad_antennas.append(antenna)
        plot_pdf(normalize(phase_data_in_degrees), antenna)


        # new_phase = transpose_by_90(phase_data_in_degrees)
        # plot_pdf(phase_data_in_degrees, "raw%s" %antenna)
        # plot_pdf(new_phase, antenna)
        # # print antenna, stats.variation(new_phase)
        # print phase_data_in_degrees
        # print new_phase

    print bad_antennas

if __name__ == "__main__":
    main()