from windpowerlib.tools import smallest_difference, linear_extra_interpolation
import pandas as pd
from pandas.util.testing import assert_series_equal


class TestTools:

    def test_smallest_difference(self):
        parameters = {'data_frame': pd.DataFrame(data={'v_wind':
                                                       [4.0, 5.0, 6.0]},
                                                 index=[100, 150, 200]),
                      'comp_value': 100,
                      'column_name': 'v_wind'}
        parameters_pd_series = {'data_frame': pd.DataFrame(data={'v_wind': [
            pd.Series(data=[4.0, 5.0, 6.0]),
            pd.Series(data=[8.0, 10.0, 14.0]),
            pd.Series(data=[16.0, 20.0, 28.0])]}, index=[100, 150, 200]),
                                'comp_value': 100,
                                'column_name': 'v_wind'}
        # TODO: test v_wind as np.array

        # comparative value is an index of data frame
        expected_output = (100, 4.0)
        assert smallest_difference(**parameters) == expected_output
        expected_series = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(smallest_difference(**parameters_pd_series)[1],
                            expected_series)
        # comparative value between indices of data frame
        expected_output = (150, 5.0)
        parameters['comp_value'], parameters_pd_series['comp_value'] = 175, 175
        assert smallest_difference(**parameters) == expected_output
        expected_series = pd.Series(data=[8.0, 10.0, 14.0])
        assert_series_equal(smallest_difference(**parameters_pd_series)[1],
                            expected_series)
        # comparative value > indices of data frame
        expected_output = (200, 6.0)
        parameters['comp_value'], parameters_pd_series['comp_value'] = 250, 250
        assert smallest_difference(**parameters) == expected_output
        expected_series = pd.Series(data=[16.0, 20.0, 28.0])
        assert_series_equal(smallest_difference(**parameters_pd_series)[1],
                            expected_series)
        # comparative value < indices of data frame
        expected_output = (100, 4.0)
        parameters['comp_value'], parameters_pd_series['comp_value'] = 90, 90
        assert smallest_difference(**parameters) == expected_output
        expected_series = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(smallest_difference(**parameters_pd_series)[1],
                            expected_series)

    def test_linear_extra_interpolation(self):
        weather = pd.DataFrame(data={'v_wind': [4.0, 5.0, 6.0]},
                               index=[100, 150, 200])
        weather_pd_series = pd.DataFrame(data={'v_wind': [
            pd.Series(data=[4.0, 5.0, 6.0]),
            pd.Series(data=[8.0, 10.0, 14.0]),
            pd.Series(data=[16.0, 20.0, 28.0])]}, index=[100, 150, 200])
        # TODO: test v_wind as np.array

        # Entries in column v_wind are float
        expected_output = 4.0
        assert (linear_extra_interpolation(weather, 100, 'v_wind') ==
                expected_output)
        expected_output = 5.5
        assert (linear_extra_interpolation(weather, 175, 'v_wind') ==
                expected_output)
        expected_output = 7.0
        assert (linear_extra_interpolation(weather, 250, 'v_wind') ==
                expected_output)
        expected_output = 3.0
        assert (linear_extra_interpolation(weather, 50, 'v_wind') ==
                expected_output)

        # Entries in column v_wind are pd.Series
        expected_output = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(linear_extra_interpolation(weather_pd_series,
                                                       100, 'v_wind'),
                            expected_output)
        expected_output = pd.Series(data=[12.0, 15.0, 21.0])
        assert_series_equal(linear_extra_interpolation(weather_pd_series,
                                                       175, 'v_wind'),
                            expected_output)
        expected_output = pd.Series(data=[24.0, 30.0, 42.0])
        assert_series_equal(linear_extra_interpolation(weather_pd_series,
                                                       250, 'v_wind'),
                            expected_output)
        expected_output = pd.Series(data=[2.0, 2.5, 2.0])  # TODO: Check this test
        assert_series_equal(linear_extra_interpolation(weather_pd_series,
                                                       75, 'v_wind'),
                            expected_output)
