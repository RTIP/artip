import casac
import numpy as np
import scipy.stats as stats
import pylab as pl

def plot_data(data):
    fit = stats.norm.pdf(data, np.mean(data), np.std(data))  #this is a fitting indeed
    pl.plot(data,fit,'-o')
    pl.hist(data,normed=True)      #use this to draw histogram of your data
    pl.ion()
    pl.show()
    pl.savefig('phase_0_0_1.png')

def main(args=None):
    ms = casac.casac.ms ()
    ms.open('/Users/dollyg/Projects/IUCAA/output/may14.ms')
    ms.selectpolarization('RR')
    ms.selectchannel(start=100)
    ms.select({'antenna1': 0, 'antenna2': 1, 'field_id': 0})

    phase_data = ms.getdata(['phase'])['phase'][0][0]

    print phase_data
    plot_data(phase_data)

if __name__ == "__main__":
    main()