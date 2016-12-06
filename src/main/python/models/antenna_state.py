from antenna_status import AntennaStatus


class AntennaState:
    def __init__(self, antenna_id, polarization, scan_id):
        self.antenna = antenna_id
        self.scan_id = scan_id
        self.polarization = polarization
        self.__closure_phase_status = None
        self.__R_phase_status = None

    def update_closure_phase_status(self, status):
        if self._can_update_status(self.__closure_phase_status, status):
            self.__closure_phase_status = status
            return True
        return False

    def get_closure_phase_status(self):
        return self.__closure_phase_status

    def update_R_phase_status(self, status):
        if self._can_update_status(self.__R_phase_status, status):
            self.__R_phase_status = status
            return True
        return False

    def _can_update_status(self, current_status, new_status):
        return (new_status in AntennaStatus.ALL) and (current_status in [None, AntennaStatus.DOUBTFUL])

    def get_R_phase_status(self):
        return self.__R_phase_status

    def __repr__(self):
        return str(self.antenna) + "" + str(self.scan_id) + str(self.polarization)