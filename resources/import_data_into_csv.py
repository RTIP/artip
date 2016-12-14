import casac
import csv
import itertools

data = {
    'input_location': '',
    'csv_location': '',
    'channel': 100,
    'polarization': 'RR',
    'antenna1': range(0,29,1),
    'antenna2': range(0,29,1),
    'scan_number': 1,
    'selection': 'corrected_amplitude'
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
                all_data = ms.getdata([data['selection']])
                amp_data = all_data[data['selection']][0][0]
                flattened_data = list(itertools.chain(*[[primary_antenna, secondary_antenna], amp_data]))
                writer.writerow(flattened_data)


main()