def is_normalized(data):
    isPositive = all(datum >= 0 for datum in data)
    isNegative = all(datum < 0 for datum in data)
    return isPositive or isNegative

def normalize(data):
    if is_normalized(data):
        return data

    def transpose(datum):
        datum=datum+90
        if(datum>=180):
            datum=datum-360
        return datum

    return map(lambda datum: transpose(datum), data)


