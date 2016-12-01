class Antenna:
    def __init__(self, antenna_id):
        self.antenna_id = antenna_id
        self.__antenna_states = []

    def add_state(self, antenna_state):
        self.__antenna_states.append(antenna_state)

    def get_states(self):
        return self.__antenna_states
