from windpowerlib.density import (temperature_gradient,
                                  rho_barometric, rho_ideal_gas)
import pandas as pd
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np


class TestDensityTemperature:

    def test_temperature_gradient(self):
        parameters = {'temp_air': pd.Series(data=[267, 268]),
                      'temp_height': 2,
                      'hub_height': 100}

        # Test temp_air as pd.Series
        temp_hub_exp = pd.Series(data=[266.363, 267.36300])
        assert_series_equal(temperature_gradient(**parameters), temp_hub_exp)

        # Test temp_air as np.array
        temp_hub_exp = np.array([266.363, 267.36300])
        parameters['temp_air'] = np.array(parameters['temp_air'])
        assert_array_equal(temperature_gradient(**parameters), temp_hub_exp)
        assert isinstance(temperature_gradient(**parameters), np.ndarray)

#    def test_temperature_interpol(self): # temperature_interpol() will be removed
#        self.weather = {'temp_air': pd.Series(data=[267, 268]),
#                        'temp_air_2': pd.Series(data=[267, 266]),
#                        'pressure': pd.Series(data=[101125, 101000])}
#        self.data_height = {'temp_air': 2,
#                            'temp_air_2': 10,
#                            'pressure': 0}
#        # Test pandas.Series
#        temp_hub_exp = pd.Series(data=[267.0, 243.5])
#        assert_series_equal(
#            temperature_interpol(self.weather['temp_air'],
#                                 self.weather['temp_air_2'],
#                                 self.data_height['temp_air'],
#                                 self.data_height['temp_air_2'],
#                                 self.h_hub),
#            temp_hub_exp)
#        # Test numpy array
#        assert_array_equal(
#            temperature_interpol(np.array(self.weather['temp_air']),
#                                 np.array(self.weather['temp_air_2']),
#                                 self.data_height['temp_air'],
#                                 self.data_height['temp_air_2'],
#                                 self.h_hub),
#            temp_hub_exp)

    def test_rho_barometric(self):
        parameters = {'pressure': pd.Series(data=[101125, 101000]),
                      'pressure_height': 0,
                      'hub_height': 100,
                      'temp_hub': pd.Series(data=[267, 268])}

        # Test pressure as pd.Series and temp_hub as pd.Series and np.array
        rho_exp = pd.Series(data=[1.30305336, 1.29656645])
        assert_series_equal(rho_barometric(**parameters), rho_exp)
        parameters['temp_hub'] = np.array(parameters['temp_hub'])
        assert_series_equal(rho_barometric(**parameters), rho_exp)

        # Test pressure as np.array and temp_hub as pd.Series
        parameters['pressure'] = np.array(parameters['pressure'])
        parameters['temp_hub'] = pd.Series(data=parameters['temp_hub'])
        assert_series_equal(rho_barometric(**parameters), rho_exp)

        # Test pressure as np.array and temp_hub as np.array
        rho_exp = np.array([1.30305336, 1.29656645])
        parameters['temp_hub'] = np.array(parameters['temp_hub'])
        assert_allclose(rho_barometric(**parameters), rho_exp)
        assert isinstance(rho_barometric(**parameters), np.ndarray)

    def test_rho_ideal_gas(self):
        parameters = {'pressure': pd.Series(data=[101125, 101000]),
                      'pressure_height': 0,
                      'hub_height': 100,
                      'temp_hub': pd.Series(data=[267, 268])}

        # Test pressure as pd.Series and temp_hub as pd.Series and np.array
        rho_exp = pd.Series(data=[1.30309439, 1.29660728])
        assert_series_equal(rho_ideal_gas(**parameters), rho_exp)
        parameters['temp_hub'] = np.array(parameters['temp_hub'])
        assert_series_equal(rho_ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temp_hub as pd.Series
        parameters['pressure'] = np.array(parameters['pressure'])
        parameters['temp_hub'] = pd.Series(data=parameters['temp_hub'])
        assert_allclose(rho_ideal_gas(**parameters), rho_exp)

        # Test pressure as np.array and temp_hub as np.array
        rho_exp = np.array([1.30309439, 1.29660728])
        parameters['temp_hub'] = np.array(parameters['temp_hub'])
        assert_allclose(rho_ideal_gas(**parameters), rho_exp)
        assert isinstance(rho_ideal_gas(**parameters), np.ndarray)
