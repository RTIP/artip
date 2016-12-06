class Antenna:
    def __init__(self, antenna_id):
        self.id = antenna_id
        self.__antenna_states = []

    def add_state(self, antenna_state):
        self.__antenna_states.append(antenna_state)

    def get_states(self):
        return self.__antenna_states

    def get_state_for(self, polarization, scan_id):

        def state_filter(state) :
            return state.polarization == polarization and state.scan_id == scan_id

        filtered_states = filter(state_filter , self.__antenna_states)
        return filtered_states[0]

    def __repr__(self):
        return str(self.id) + str(self.__antenna_states)
