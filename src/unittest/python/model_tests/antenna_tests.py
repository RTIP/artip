from unittest import TestCase

from models.antenna import Antenna


class AntennaTest(TestCase):
    def test_should_add_state_of_an_antenna(self):
        antenna = Antenna('some_id')
        antenna.add_state('some_state')
        self.assertListEqual(antenna.get_states(), ['some_state'])

    def test_should_return_states_of_an_antenna(self):
        antenna = Antenna('id')
        antenna.add_state('state_one')
        antenna.add_state('state_two')
        self.assertItemsEqual(antenna.get_states(), ['state_one', 'state_two'])
