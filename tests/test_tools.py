from windpowerlib.tools import smallest_difference
import collections


class TestTools:

    @classmethod
    def setup_class(self):
        self.return_tuple = collections.namedtuple('selected_values',
                                                   ['closest_value',
                                                    'corresp_value'])

    def test_smallest_difference(self):
        # value_1 closer to comparative value
        expected_output = self.return_tuple(30, 5.0)
        assert smallest_difference(30, 10, 100, 5.0, 6.0) == expected_output
        # value_1 = comparative value
        expected_output = self.return_tuple(100, 5.0)
        assert smallest_difference(100, 10, 100, 5.0, 6.0) == expected_output
        # value_2 closer to comparative value
        expected_output = self.return_tuple(30, 6.0)
        assert smallest_difference(10, 30, 100, 5.0, 6.0) == expected_output
        # value_2 = comparative value
        expected_output = self.return_tuple(100, 6.0)
        assert smallest_difference(10, 100, 100, 5.0, 6.0) == expected_output
        # value_2 is None
        expected_output = self.return_tuple(10, 5.0)
        assert smallest_difference(10, None, 100, 5.0, 6.0) == expected_output
