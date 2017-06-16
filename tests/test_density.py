from windpowerlib.density import (temperature_gradient,
                                  rho_barometric, rho_ideal_gas)
import pandas as pd
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np


class TestDensityTemperature:

    def test_temperature_gradient(self):
        parameters = {'temperature': pd.Series(data=[267, 268]),
                      'temperature_height': 2,
                      'hub_height': 100}

        # Test temperature as pd.Series
        temp_hub_exp = pd.Series(data=[266.363, 267.36300])
        assert_series_equal(temperature_gradient(**parameters), temp_hub_exp)

        # Test temperature as np.array
        temp_hub_exp = np.array([266.363, 267.36300])
        parameters['temperature'] = np.array(parameters['temperature'])
        assert_array_equal(temperature_gradient(**parameters), temp_hub_exp)
        assert isinstance(temperature_gradient(**parameters), np.ndarray)

    def test_rho_barometric(self):
        parameters = {'pressure': pd.Series(data=[101125, 101000]),
                      'pressure_height': 0,
                      'hub_height': 100,
                      'temperature_hub_height': pd.Series(data=[267, 268])}

        # Test pressure as pd.Series and temperature_hub_height as pd.Series
        # and np.array
        rho_exp = pd.Series(data=[1.30305336, 1.29656645])
        assert_series_equal(rho_barometric(**parameters), rho_exp)
        parameters['temperature_hub_height'] = np.array(
            parameters['temperature_hub_height'])
        assert_series_equal(rho_barometric(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as pd.Series
        parameters['pressure'] = np.array(parameters['pressure'])
        parameters['temperature_hub_height'] = pd.Series(
            data=parameters['temperature_hub_height'])
        assert_series_equal(rho_barometric(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as np.array
        rho_exp = np.array([1.30305336, 1.29656645])
        parameters['temperature_hub_height'] = np.array(
            parameters['temperature_hub_height'])
        assert_allclose(rho_barometric(**parameters), rho_exp)
        assert isinstance(rho_barometric(**parameters), np.ndarray)

    def test_rho_ideal_gas(self):
        parameters = {'pressure': pd.Series(data=[101125, 101000]),
                      'pressure_height': 0,
                      'hub_height': 100,
                      'temperature_hub_height': pd.Series(data=[267, 268])}

        # Test pressure as pd.Series and temperature_hub_height as pd.Series
        # and np.array
        rho_exp = pd.Series(data=[1.30309439, 1.29660728])
        assert_series_equal(rho_ideal_gas(**parameters), rho_exp)
        parameters['temperature_hub_height'] = np.array(
            parameters['temperature_hub_height'])
        assert_series_equal(rho_ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as pd.Series
        parameters['pressure'] = np.array(parameters['pressure'])
        parameters['temperature_hub_height'] = pd.Series(
            data=parameters['temperature_hub_height'])
        assert_allclose(rho_ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temperature_hub_height as np.array
        rho_exp = np.array([1.30309439, 1.29660728])
        parameters['temperature_hub_height'] = np.array(
            parameters['temperature_hub_height'])
        assert_allclose(rho_ideal_gas(**parameters), rho_exp)
        assert isinstance(rho_ideal_gas(**parameters), np.ndarray)
