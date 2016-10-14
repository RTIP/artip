
def shift_data_to_zero(data):

    def transpose(datum):
        if datum>=0:
            return datum-180
        else:
            return datum+180

    return map(lambda datum:transpose(datum),data)

def is_data_near_180(data):
    positive_phases = filter(lambda datum: datum>=0, data)
    negative_phases = filter(lambda datum: datum<0, data)

    min_of_range = min(positive_phases)
    max_of_range = max(negative_phases)

    return min_of_range>90 and max_of_range<-90

def convert_phase_to_positives(data):
    delta_to_shift = min(data)
    return map(lambda datum: datum + abs(delta_to_shift), data)


def shift_linear(data):
    if is_data_near_180(data):
        data = shift_data_to_zero(data)

    shifted_phases = convert_phase_to_positives(data)
    shifted_phases.sort()
    return shifted_phases