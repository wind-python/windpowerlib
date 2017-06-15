from windpowerlib.tools import smallest_difference, linear_extra_interpolation
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal


class TestTools:

    def test_smallest_difference(self):
        data_frame = pd.DataFrame(data={'v_wind': [4.0, 5.0, 6.0]},
                                  index=[100, 150, 200])
        data_frame_series = pd.DataFrame(data={'v_wind': [
            pd.Series(data=[4.0, 5.0, 6.0]),
            pd.Series(data=[8.0, 10.0, 14.0]),
            pd.Series(data=[16.0, 20.0, 28.0])]}, index=[100, 150, 200])
        data_frame_arr = pd.DataFrame(data={'v_wind': [
            np.array(data_frame_series['v_wind'][data_frame_series.index[0]]),
            np.array(data_frame_series['v_wind'][data_frame_series.index[1]]),
            np.array(data_frame_series['v_wind'][data_frame_series.index[2]])]},
                                   index=data_frame_series.index)
        parameters = {'comp_value': 100,
                      'column_name': 'v_wind'}

        # comparative value is an index of data frame
        exp_output = (100, 4.0)
        assert smallest_difference(data_frame, **parameters) == exp_output
        exp_series = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(smallest_difference(data_frame_series,
                                                **parameters)[1], exp_series)
        exp_arr = np.array(exp_series)
        assert_array_equal(smallest_difference(data_frame_arr,
                                               **parameters)[1], exp_arr)
        # comparative value between indices of data frame
        exp_output = (150, 5.0)
        parameters['comp_value'] = 175
        assert smallest_difference(data_frame, **parameters) == exp_output
        exp_series = pd.Series(data=[8.0, 10.0, 14.0])
        assert_series_equal(smallest_difference(data_frame_series,
                                                **parameters)[1], exp_series)
        exp_arr = np.array(exp_series)
        assert_array_equal(smallest_difference(data_frame_arr,
                                               **parameters)[1], exp_arr)
        # comparative value > indices of data frame
        exp_output = (200, 6.0)
        parameters['comp_value'] = 250
        assert smallest_difference(data_frame, **parameters) == exp_output
        exp_series = pd.Series(data=[16.0, 20.0, 28.0])
        assert_series_equal(smallest_difference(data_frame_series,
                                                **parameters)[1], exp_series)
        exp_arr = np.array(exp_series)
        assert_array_equal(smallest_difference(data_frame_arr,
                                               **parameters)[1], exp_arr)
        # comparative value < indices of data frame
        exp_output = (100, 4.0)
        parameters['comp_value'] = 90
        assert smallest_difference(data_frame, **parameters) == exp_output
        exp_series = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(smallest_difference(data_frame_series,
                                                **parameters)[1], exp_series)
        exp_arr = np.array(exp_series)
        assert_array_equal(smallest_difference(data_frame_arr,
                                               **parameters)[1], exp_arr)

    def test_linear_extra_interpolation(self):
        parameters = {'requested_height': 100,
                      'column_name': 'v_wind'}
        data_frame = pd.DataFrame(data={'v_wind': [4.0, 5.0, 6.0]},
                                  index=[100, 150, 200])
        data_frame_series = pd.DataFrame(data={'v_wind': [
            pd.Series(data=[4.0, 5.0, 6.0]),
            pd.Series(data=[8.0, 10.0, 14.0]),
            pd.Series(data=[16.0, 20.0, 28.0])]}, index=[100, 150, 200])
        # TODO: test v_wind as np.array

        # requested_height is an index of data frame
        exp_output = 4.0
        assert (linear_extra_interpolation(data_frame, **parameters) ==
                exp_output)
        exp_output = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(linear_extra_interpolation(data_frame_series,
                                                       **parameters),
                            exp_output)
        # requested_height is between indices of data frame
        exp_output = 5.5
        parameters['requested_height'] = 175
        assert (linear_extra_interpolation(data_frame, **parameters) ==
                exp_output)
        exp_output = pd.Series(data=[12.0, 15.0, 21.0])
        assert_series_equal(linear_extra_interpolation(data_frame_series,
                                                       **parameters),
                            exp_output)
        # requested_height > indices of data frame
        exp_output = 7.0
        parameters['requested_height'] = 250
        assert (linear_extra_interpolation(data_frame, **parameters) ==
                exp_output)
        exp_output = pd.Series(data=[24.0, 30.0, 42.0])
        assert_series_equal(linear_extra_interpolation(data_frame_series,
                                                       **parameters),
                            exp_output)
        # requested_height is < indices of data frame
        exp_output = 3.0
        parameters['requested_height'] = 50
        assert (linear_extra_interpolation(data_frame, **parameters) ==
                exp_output)
        parameters['requested_height'] = 75
        exp_output = pd.Series(data=[2.0, 2.5, 2.0])
        assert_series_equal(linear_extra_interpolation(data_frame_series,
                                                       **parameters),
                            exp_output)
        # TODO: Check this test