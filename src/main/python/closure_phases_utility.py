import casac
import numpy


class ClosurePhaseUtil:
    def __init__(self, source):
        self.__ms = casac.casac.ms()
        self.__ms.open(source)
        self.__metadata = self.__ms.metadata()

    def __del__(self):
        self.__ms.close()

    def closurePhTriads(self, msname, triadlist, chan={}):
        ms = casac.casac.ms()
        ms.open(msname)
        if chan: ms.selectchannel(**chan)
        # Note the use of ifraxis. This means time and interfoerometer
        # number are separate dimensions in the returned data
        dd = ms.getdata(["antenna1", "antenna2", "phase"], ifraxis=True)
        ph = dd["phase"];
        a1 = dd["antenna1"];
        a2 = dd["antenna2"]
        ms.close()
        res = []
        for tr in triadlist:
            ((p1, p2, p3),
             (s1, s2, s3)) = self.triadRows(a1, a2, tr)
            phr = self.rewrap(ph[:, :, p1, :] * s1 + ph[:, :, p2, :] * s2 + ph[:, :, p3, :] * s3)
            res.append(phr)
        return numpy.array(res)

    def rewrap(self, p):
        return numpy.arctan2(numpy.sin(p), numpy.cos(p))

    def eitherWay(self, a1, a2, i, j):
        """Return rows where a1==i and a2==j OR a1==j and a2==i. Also return
        sign +1 if former or -1 if latter.
        """
        r1 = numpy.logical_and(a1 == i, a2 == j).nonzero()[0]
        if r1.shape[0]:
            return r1[0], +1.0
        else:
            return numpy.logical_and(a1 == j, a2 == i).nonzero()[0][0], -1.0

    def triadRows(self, a1, a2, tr):
        """
        Rows corresponding to single triad tr
        """
        i, j, k = tr
        p1, s1 = self.eitherWay(a1, a2, i, j)
        p2, s2 = self.eitherWay(a1, a2, j, k)
        p3, s3 = self.eitherWay(a1, a2, k, i)
        return ((p1, p2, p3),
                (s1, s2, s3))
