from unittest import TestCase

from models.antenna_state import AntennaState
from models.antenna_status import AntennaStatus


class AntennaStatesTest(TestCase):
    def test_should_update_closure_phase_status_of_antenna(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        self.assertTrue(antenna_state.update_closure_phase_status(AntennaStatus.GOOD))

    def test_should_update_closure_phase_status_if_current_status_is_doubtful(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_closure_phase_status(AntennaStatus.DOUBTFUL)
        self.assertTrue(antenna_state.update_closure_phase_status(AntennaStatus.GOOD))

    def test_should_not_update_closure_phase_status_if_current_status_is_not_doubtful(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_closure_phase_status(AntennaStatus.GOOD)
        self.assertFalse(antenna_state.update_closure_phase_status(AntennaStatus.GOOD))

    def test_should_not_update_closure_phase_status_for_invalid_value(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        self.assertFalse(antenna_state.update_closure_phase_status('invalid'))

    def test_should_update_R_phase_status_of_antenna(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        self.assertTrue(antenna_state.update_R_phase_status(AntennaStatus.GOOD))

    def test_should_update_R_phase_status_if_current_status_is_doubtful(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_R_phase_status(AntennaStatus.DOUBTFUL)
        self.assertTrue(antenna_state.update_R_phase_status(AntennaStatus.GOOD))

    def test_should_not_update_R_phase_status_if_current_status_is_not_doubtful(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_R_phase_status(AntennaStatus.GOOD)
        self.assertFalse(antenna_state.update_R_phase_status(AntennaStatus.BAD))

    def test_should_not_update_R_phase_status_for_invalid_value(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        self.assertFalse(antenna_state.update_R_phase_status('invalid'))

    def test_should_return_R_phase_status(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_R_phase_status(AntennaStatus.GOOD)
        self.assertEquals(antenna_state.get_R_phase_status(), AntennaStatus.GOOD)

    def test_return_closure_phase_status(self):
        antenna_state = AntennaState('antenna_id', 'polarization', 'scan_id')
        antenna_state.update_closure_phase_status(AntennaStatus.GOOD)
        self.assertEquals(antenna_state.get_closure_phase_status(), AntennaStatus.GOOD)