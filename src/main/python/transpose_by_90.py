from linearshifting import is_normalized

def transpose_by_90(data):
    if is_normalized(data):
        return data
    def transpose(datum):
        datum=datum+90
        if(datum>=180):
            datum=datum-360
        return datum

    return map(lambda datum: transpose(datum), data)

def is_dispersed(data):
    max_of_range = max(data)
    min_of_range = min(data)

    return max_of_range-min_of_range >100

def normalize(data):
    max_no_of_transposes = 1
    no_of_transposes_done = 0
    print data
    while no_of_transposes_done < max_no_of_transposes:
        if is_dispersed(data):
            data=transpose_by_90(data)
            print data
        else:
            return data
        no_of_transposes_done += 1
    return data



def is_good(data):
    normalized_data = normalize(data)
    return not is_dispersed(normalized_data)
