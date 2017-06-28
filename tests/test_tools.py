from windpowerlib.tools import linear_interpolation_extrapolation
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal


class TestTools:

    def test_linear_interpolation_extrapolation(self):
        parameters = {'target_height': 80}
        df = pd.DataFrame(data={10: [2.0, 2.0, 3.0],
                                80: [4.0, 5.0, 6.0],
                                200: [5.0, 8.0, 10.0]},
                          index=[0, 1, 2])
        # target_height is equal to height given in a column of the DataFrame
        exp_output = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(linear_interpolation_extrapolation(
            df, **parameters), exp_output)
        # target_height is between heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(data=[4.5, 6.5, 8.0])
        parameters['target_height'] = 140
        assert_series_equal(linear_interpolation_extrapolation(
            df, **parameters), exp_output)
        exp_output = pd.Series(data=[4.285714, 5.428571, 6.428571])
        parameters['target_height'] = 90
        assert_series_equal(linear_interpolation_extrapolation(
            df, **parameters), exp_output)
        # target_height is greater than the heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(data=[5.333333, 9.0, 11.333333])
        parameters['target_height'] = 240
        assert_series_equal(linear_interpolation_extrapolation(
            df, **parameters), exp_output)
        # target_height is smaller than the heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(data=[1.857143, 1.785714, 2.785714])
        parameters['target_height'] = 5
        assert_series_equal(linear_interpolation_extrapolation(
            df, **parameters), exp_output)
