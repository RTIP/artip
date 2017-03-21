import numpy

ms.open('../MS_DATASET/may30.ms')
ms.selectinit(reset=True)
# ms.selectpolarization('RR')
ms.select({'antenna1': 0, 'antenna2': 12, 'field_id': 0, 'scan_number': 1})
data_with_flags = ms.getdata(['corrected_data', 'flag'])
data = data_with_flags['corrected_data']
flags = data_with_flags['flag']

AverageReal = 0
AverageImag = 0
StdReal = 1000.0
StdImag = 1000.0
SumWeightReal = 0
SumWeightImag = 0
scutoff_sum = [0] * 512
scutoff_sum_count = [0] * 512
scutoff_sum_squares = [0] * 512

realVisForMedian = []
imagVisForMedian = []
winsize = 5
total_timestamps = 56
effective_center = (int)(winsize - 1) / 2
scutof = 19.41367489
spectralmax_p = 10000000
spectralmin_p = -10

for timestep in range(effective_center, total_timestamps - effective_center):
    for pol in range(0, 2):
        realVisForMedian = []
        imagVisForMedian = []

        for chan in range(0, 512):
            visibility = data[pol][chan][timestep]
            realVisForMedian.append(visibility.real)
            imagVisForMedian.append(visibility.imag)
            SumWeightReal += 1
            SumWeightImag += 1

        if SumWeightReal > 0:
            AverageReal = numpy.median(realVisForMedian)
            AverageImag = numpy.median(imagVisForMedian)

            numpy.subtract(realVisForMedian, AverageReal)
            numpy.subtract(imagVisForMedian, AverageImag)

            StdReal = 1.4826 * numpy.median(realVisForMedian)
            StdImag = 1.4826 * numpy.median(imagVisForMedian)

        if scutof < 0:
            for chan in range(0, 512):
                if flags[pol][chan][timestep]: continue
                visibility = data[pol][chan][timestep]

                if SumWeightReal > 0:
                    deviationReal = abs(visibility.real - AverageReal)
                    scutoff_sum_count[chan] += 1
                    scutoff_sum[chan] += deviationReal
                    scutoff_sum_squares[chan] += deviationReal * deviationReal

                if SumWeightImag > 0:
                    deviationImag = abs(visibility.imag - AverageImag)
                    scutoff_sum_count[chan] += 1
                    scutoff_sum[chan] += deviationImag
                    scutoff_sum_squares[chan] += deviationImag * deviationImag
        else:
            if (StdReal > spectralmax_p) or (StdImag > spectralmax_p) or (StdReal < spectralmin_p) or (
                        StdImag < spectralmin_p):

                for chan in range(0, 512):
                    print "Flagging", chan, pol, timestep, "Std Real :", StdReal, "StdImag :", StdImag
            else:
                visibility = data[pol][chan][timestep]

                if (abs(visibility.real - AverageReal) > scutof) or (abs(visibility.imag - AverageImag) > scutof):
                    print "Flagging", chan, pol, timestep, abs(visibility.real - AverageReal), abs(
                        visibility.imag - AverageImag)
