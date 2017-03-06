class Antenna:
    def __init__(self, antenna_id):
        self.id = antenna_id
        self.__antenna_states = []

    def add_state(self, antenna_state):
        self.__antenna_states.append(antenna_state)

    def get_states(self, scan_ids=None):
        if scan_ids:
            return filter(lambda state: state.scan_id in scan_ids, self.__antenna_states)
        return self.__antenna_states

    def get_state_for(self, polarization, scan_id):
        def state_filter(state):
            return state.polarization == polarization and state.scan_id == scan_id

        filtered_states = filter(state_filter, self.__antenna_states)
        return filtered_states[0]

    def update_state(self, polarization, scan_id, status):
        current_state = self.get_state_for(polarization, scan_id)
        current_state.update_R_phase_status(status)

    def __repr__(self):
        return "A" + str(self.id)
