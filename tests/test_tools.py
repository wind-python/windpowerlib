from windpowerlib.tools import smallest_difference
import pandas as pd


class TestTools:

    def test_smallest_difference(self):
        parameters = {'data_frame': pd.DataFrame(data={'v_wind':
                                                       [4.0, 5.0, 6.0]},
                                                 index=[100, 150, 200]),
                      'comp_value': 100,
                      'column_name': 'v_wind'}
        # TODO: test v_wind as pd.Series and np.array

        # comparative value is an index of data frame
        expected_output = (100, 4.0)
        assert smallest_difference(**parameters) == expected_output
        # comparative value between indices of data frame
        expected_output = (150, 5.0)
        parameters['comp_value'] = 175
        assert smallest_difference(**parameters) == expected_output
        # comparative value > indices of data frame
        expected_output = (200, 6.0)
        parameters['comp_value'] = 250
        assert smallest_difference(**parameters) == expected_output
        # comparative value < indices of data frame
        expected_output = (100, 4.0)
        parameters['comp_value'] = 90
        assert smallest_difference(**parameters) == expected_output
