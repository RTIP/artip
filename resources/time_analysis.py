import numpy

ms.open('~/Downloads/MS_DATASET/may30.ms')
ms.selectinit(reset=True)
# ms.selectpolarization('RR')
ms.select({'antenna1': 2, 'antenna2': 11, 'field_id': [0], 'scan_number': 1})
data_with_flags = ms.getdata(['corrected_data', 'flag'])
data = data_with_flags['corrected_data']
flags = data_with_flags['flag']
timedev = 3.26948
winsize = 3
total_timestamps = 55
effective_center = (int)(winsize - 1) / 2
winstart = effective_center
noise_sum = [0] * 512
noise_sum_count = [0] * 512
noise_sum_squares = [0] * 512
count = 0
print "chan | pol | CentralTime | StdTotal\t"
for i in range(effective_center, total_timestamps - effective_center):
    for chan in range(0, 512):
        for pol in range(0, 2):
            SumWeight = 0
            StdTotal = 0
            SumReal = 0
            SumRealSquare = 0
            AverageReal = 0
            StdReal = 0
            SumImag = 0
            SumImagSquare = 0
            AverageImag = 0
            StdImag = 0
            for timestep in (i - effective_center, i + effective_center):
                if flags[pol][chan][timestep]:
                    continue
                visibility = data[pol][chan][timestep]
                SumWeight += 1
                SumReal += visibility.real
                SumRealSquare += visibility.real * visibility.real
                SumImag += visibility.imag
                SumImagSquare += visibility.imag * visibility.imag
            if SumWeight > 0:
                AverageReal = SumReal / SumWeight
                AvgRealSquare = SumRealSquare / SumWeight
                StdReal = AvgRealSquare - AverageReal * AverageReal
                AverageImag = SumImag / SumWeight
                SumImagSquare = SumImagSquare / SumWeight
                StdImag = SumImagSquare - AverageImag * AverageImag
                StdTotal = numpy.sqrt(StdReal + StdImag)
                noise_sum[chan] += StdTotal
                noise_sum_squares[chan] += StdTotal * StdTotal
                noise_sum_count[chan] += 1
                if StdTotal > timedev:
                # if chan in range(25, 80) and pol == 1:
                    count += 1
                    print chan, "\t", pol, "\t", i, "\t", StdTotal

print "Total times flagged, ", count
