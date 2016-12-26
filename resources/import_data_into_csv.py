import casac
import csv
import itertools

data = {
    'input_location': '/Users/dollyg/Projects/IUCAA/output/aug7.ms',
    'csv_location': '/Users/dollyg/Projects/IUCAA/output/aug7.csv',
    'channel': 100,
    'polarization': 'RR',
    'antenna1': range(0,29,1),
    'antenna2': range(0,29,1),
    'scan_number': 1,
    'selection': 'time'
}


def main(args=None):
    ms = casac.casac.ms ()
    ms.open(data['input_location'])
    with open(data['csv_location'], 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for antenna1 in data['antenna1']:
            for antenna2 in data['antenna2']:
                ms.selectinit(reset=True)
                ms.selectpolarization(data['polarization'])
                ms.selectchannel(start=data['channel'])

                if antenna1 == antenna2:
                    continue
                elif antenna1 < antenna2:
                    primary_antenna = antenna1
                    secondary_antenna = antenna2
                else:
                    primary_antenna = antenna2
                    secondary_antenna = antenna1

                ms.select({'scan_number': data['scan_number'], 'antenna1': primary_antenna, 'antenna2': secondary_antenna})
                all_data = ms.getdata(data['selection'])
                print all_data
                # amp_data = all_data[data['selection']][0][0]
                # time_data = all_data[data['selection'][1]][0][0]
                # print "time=",time_data
                # print amp_data
                flattened_data = list(itertools.chain(*[[primary_antenna, secondary_antenna], amp_data]))
                writer.writerow(flattened_data)


main()