import casac
import csv

inputs = {
    'input_location': '/Users/artip/Projects/iucaa/artip/data/copies/may14.ms',
    'csv_location': '/Users/artip/Projects/iucaa/artip/data/copies/may14.csv',
    'channel': 100,
    'polarization': 'RR',
    'antenna1': range(0, 29, 1),
    'antenna2': range(0, 29, 1),
    'scan_number': 1,
    'selection': ['amplitude', 'time', 'antenna1', 'antenna2']
}


def get_data():
    ms = casac.casac.ms()
    ms.open(inputs['input_location'])
    ms.selectinit(reset=True)
    ms.selectpolarization(inputs['polarization'])
    ms.selectchannel(start=inputs['channel'])
    ms.select({'scan_number': inputs['scan_number']})
    all_data = ms.getdata(inputs['selection'])
    antenna1s = list(map(lambda antenna: int(antenna), all_data['antenna1']))
    antenna2s = list(map(lambda antenna: int(antenna), all_data['antenna2']))
    times = list(map(lambda time: float(time), all_data['time']))
    amp_data = list(map(lambda amp: float(amp), all_data['amplitude'][0][0]))
    return list(zip(antenna1s, antenna2s, times, amp_data))



def main(args=None):
    with open(inputs['csv_location'], 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(get_data())


main()