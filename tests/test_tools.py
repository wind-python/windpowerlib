"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import pandas as pd
from pandas.testing import assert_series_equal

from windpowerlib.tools import (
    linear_interpolation_extrapolation,
    logarithmic_interpolation_extrapolation,
)


class TestTools:
    @classmethod
    def setup_class(cls):
        cls.parameters = {"target_height": 80}
        cls.df = pd.DataFrame(
            data={
                10: [2.0, 2.0, 3.0],
                80: [4.0, 5.0, 6.0],
                200: [5.0, 8.0, 10.0],
            },
            index=[0, 1, 2],
        )

    def test_linear_target_height_is_equal_to_given_height(self):
        """
        Test linear interpolation and extrapolation if target_height is equal
        to height given in a column of the DataFrame.
        """
        exp_output = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(
            linear_interpolation_extrapolation(self.df, **self.parameters),
            exp_output,
        )

    def test_linear_target_height_is_between_given_heights(self):
        """
        Test linear interpolation and extrapolation if target_height is between
        heights given in the columns of the DataFrame
        """
        exp_output = pd.Series(data=[4.5, 6.5, 8.0])
        self.parameters["target_height"] = 140
        assert_series_equal(
            linear_interpolation_extrapolation(self.df, **self.parameters),
            exp_output,
        )

        exp_output = pd.Series(data=[4.285714, 5.428571, 6.428571])
        self.parameters["target_height"] = 90
        assert_series_equal(
            linear_interpolation_extrapolation(self.df, **self.parameters),
            exp_output,
        )

    def test_linear_target_height_is_greater_than_the_given_heights(self):
        """
        Test linear interpolation and extrapolation if target_height is greater
        than the heights given in the columns of the DataFrame
        """
        exp_output = pd.Series(data=[5.333333, 9.0, 11.333333])
        self.parameters["target_height"] = 240
        assert_series_equal(
            linear_interpolation_extrapolation(self.df, **self.parameters),
            exp_output,
        )

    def test_linear_target_height_is_smaller_than_the_given_heights(self):
        """
        Test linear interpolation and extrapolation if target_height is smaller
        than the heights given in the columns of the DataFrame
        """
        exp_output = pd.Series(data=[1.857143, 1.785714, 2.785714])
        self.parameters["target_height"] = 5
        assert_series_equal(
            linear_interpolation_extrapolation(self.df, **self.parameters),
            exp_output,
        )

    def test_logarithmic_interpolation_extrapolation(self):
        parameters = {"target_height": 80}
        df = pd.DataFrame(
            data={
                10: [2.0, 2.0, 3.0],
                80: [4.0, 5.0, 6.0],
                200: [5.0, 8.0, 10.0],
            },
            index=[0, 1, 2],
        )
        # target_height is equal to height given in a column of the DataFrame
        exp_output = pd.Series(data=[4.0, 5.0, 6.0])
        assert_series_equal(
            logarithmic_interpolation_extrapolation(df, **parameters),
            exp_output,
        )
        # target_height is between heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(
            data=[4.61074042165, 6.83222126494, 8.44296168659]
        )
        parameters["target_height"] = 140
        assert_series_equal(
            logarithmic_interpolation_extrapolation(df, **parameters),
            exp_output,
        )
        exp_output = pd.Series(
            data=[4.11328333429, 5.16992500144, 6.16992500144]
        )
        parameters["target_height"] = 90
        assert_series_equal(
            logarithmic_interpolation_extrapolation(df, **parameters),
            exp_output,
        )
        # target_height is greater than the heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(
            data=[5.19897784672, 8.59693354015, 10.7959113869]
        )
        parameters["target_height"] = 240
        assert_series_equal(
            logarithmic_interpolation_extrapolation(df, **parameters),
            exp_output,
        )
        # target_height is smaller than the heights given in the columns of the
        # DataFrame
        exp_output = pd.Series(data=[1.33333333333, 1.0, 2.0])
        parameters["target_height"] = 5
        assert_series_equal(
            logarithmic_interpolation_extrapolation(df, **parameters),
            exp_output,
        )
