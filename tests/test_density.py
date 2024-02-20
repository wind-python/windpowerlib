"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal
from numpy.testing import assert_allclose

from windpowerlib.density import barometric, ideal_gas


class TestDensity:
    def test_barometric(self):
        parameters = {
            "pressure": pd.Series(data=[101125, 101000]),
            "pressure_height": 0,
            "hub_height": 100,
            "temperature_hub_height": pd.Series(data=[267, 268]),
        }

        # Test pressure as pd.Series and temperature_hub_height as pd.Series
        # and np.array
        rho_exp = pd.Series(data=[1.30305336, 1.29656645])
        assert_series_equal(barometric(**parameters), rho_exp)
        parameters["temperature_hub_height"] = np.array(
            parameters["temperature_hub_height"]
        )
        assert_series_equal(barometric(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as pd.Series
        parameters["pressure"] = np.array(parameters["pressure"])
        parameters["temperature_hub_height"] = pd.Series(
            data=parameters["temperature_hub_height"]
        )
        assert_series_equal(barometric(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as np.array
        rho_exp = np.array([1.30305336, 1.29656645])
        parameters["temperature_hub_height"] = np.array(
            parameters["temperature_hub_height"]
        )
        assert_allclose(barometric(**parameters), rho_exp)
        assert isinstance(barometric(**parameters), np.ndarray)

    def test_ideal_gas(self):
        parameters = {
            "pressure": pd.Series(data=[101125, 101000]),
            "pressure_height": 0,
            "hub_height": 100,
            "temperature_hub_height": pd.Series(data=[267, 268]),
        }

        # Test pressure as pd.Series and temperature_hub_height as pd.Series
        # and np.array
        rho_exp = pd.Series(data=[1.30309439, 1.29660728])
        assert_series_equal(ideal_gas(**parameters), rho_exp)
        parameters["temperature_hub_height"] = np.array(
            parameters["temperature_hub_height"]
        )
        assert_series_equal(ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as pd.Series
        parameters["pressure"] = np.array(parameters["pressure"])
        parameters["temperature_hub_height"] = pd.Series(
            data=parameters["temperature_hub_height"]
        )
        assert_allclose(ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as np.array
        rho_exp = np.array([1.30309439, 1.29660728])
        parameters["temperature_hub_height"] = np.array(
            parameters["temperature_hub_height"]
        )
        assert_allclose(ideal_gas(**parameters), rho_exp)
        assert isinstance(ideal_gas(**parameters), np.ndarray)
