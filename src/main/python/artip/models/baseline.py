class Baseline:
    def __init__(self, antenna1, antenna2):
        self.antenna1 = int(antenna1)
        self.antenna2 = int(antenna2)

    def __repr__(self):
        return str(self.antenna1) + "-" + str(self.antenna2)

    def __str__(self):
        return str(self.antenna1) + "&" + str(self.antenna2)

    def __eq__(self, other):
        return other.__dict__ == self.__dict__

    def __hash__(self):
        return hash(tuple([self.antenna1, self.antenna2]))

    def contains(self, antenna_id):
        return self.antenna1==antenna_id or self.antenna2==antenna_id
