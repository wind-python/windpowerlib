"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import pandas as pd
import numpy as np
import pytest
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_allclose

from windpowerlib.wind_speed import logarithmic_profile, hellman


class TestWindSpeed:
    def test_logarithmic_profile(self):
        parameters = {
            "wind_speed": pd.Series(data=[5.0, 6.5]),
            "wind_speed_height": 10,
            "hub_height": 100,
            "roughness_length": pd.Series(data=[0.15, 0.15]),
            "obstacle_height": 0,
        }

        # Test wind_speed as pd.Series with roughness_length as pd.Series,
        # np.array and float
        v_wind_hub_exp = pd.Series(data=[7.74136523, 10.0637748])
        assert_series_equal(logarithmic_profile(**parameters), v_wind_hub_exp)
        parameters["roughness_length"] = np.array(
            parameters["roughness_length"]
        )
        assert_series_equal(logarithmic_profile(**parameters), v_wind_hub_exp)
        parameters["roughness_length"] = parameters["roughness_length"][0]
        assert_series_equal(logarithmic_profile(**parameters), v_wind_hub_exp)

        # Test wind_speed as np.array with roughness_length as float, pd.Series
        # and np.array
        v_wind_hub_exp = np.array([7.74136523, 10.0637748])
        parameters["wind_speed"] = np.array(parameters["wind_speed"])
        assert_allclose(logarithmic_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_profile(**parameters), np.ndarray)
        parameters["roughness_length"] = pd.Series(
            data=[
                parameters["roughness_length"],
                parameters["roughness_length"],
            ]
        )
        assert_allclose(logarithmic_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_profile(**parameters), np.ndarray)
        parameters["roughness_length"] = np.array(
            parameters["roughness_length"]
        )
        assert_allclose(logarithmic_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_profile(**parameters), np.ndarray)

        # Test obstacle_height is not zero
        v_wind_hub_exp = np.array([13.54925281, 17.61402865])
        parameters["obstacle_height"] = 12
        assert_allclose(logarithmic_profile(**parameters), v_wind_hub_exp)

        # Raise ValueError due to 0.7 * `obstacle_height` > `wind_speed_height`
        with pytest.raises(ValueError):
            parameters["obstacle_height"] = 20
            logarithmic_profile(**parameters)

    def test_hellman(self):
        parameters = {
            "wind_speed": pd.Series(data=[5.0, 6.5]),
            "wind_speed_height": 10,
            "hub_height": 100,
            "roughness_length": pd.Series(data=[0.15, 0.15]),
            "hellman_exponent": None,
        }

        # Test wind_speed is pd.Series with roughness_length is pd.Series,
        # np.array and float
        v_wind_hub_exp = pd.Series(data=[7.12462437, 9.26201168])
        assert_series_equal(hellman(**parameters), v_wind_hub_exp)
        parameters["roughness_length"] = np.array(
            parameters["roughness_length"]
        )
        assert_series_equal(hellman(**parameters), v_wind_hub_exp)
        parameters["roughness_length"] = parameters["roughness_length"][0]
        assert_series_equal(hellman(**parameters), v_wind_hub_exp)

        # Test wind_speed as np.array with roughness_length is float, pd.Series
        # and np.array
        v_wind_hub_exp = np.array([7.12462437, 9.26201168])
        parameters["wind_speed"] = np.array(parameters["wind_speed"])
        assert_allclose(hellman(**parameters), v_wind_hub_exp)
        assert isinstance(hellman(**parameters), np.ndarray)
        parameters["roughness_length"] = pd.Series(
            data=(
                parameters["roughness_length"],
                parameters["roughness_length"],
            )
        )
        assert_allclose(hellman(**parameters), v_wind_hub_exp)
        assert isinstance(hellman(**parameters), np.ndarray)
        parameters["roughness_length"] = np.array(
            parameters["roughness_length"]
        )
        assert_allclose(hellman(**parameters), v_wind_hub_exp)
        assert isinstance(hellman(**parameters), np.ndarray)

        # Test roughness_length is None and hellman_exponent is None
        v_wind_hub_exp = pd.Series(data=[6.9474774, 9.03172])
        parameters["wind_speed"] = pd.Series(data=parameters["wind_speed"])
        parameters["roughness_length"] = None
        assert_series_equal(hellman(**parameters), v_wind_hub_exp)

        # Test hellman_exponent is not None
        v_wind_hub_exp = pd.Series(data=[7.92446596, 10.30180575])
        parameters["roughness_length"] = 0.15
        parameters["hellman_exponent"] = 0.2
        assert_series_equal(hellman(**parameters), v_wind_hub_exp)
