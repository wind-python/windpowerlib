from windpowerlib.density import (temperature_gradient, temperature_interpol,
                                  rho_barometric, rho_ideal_gas)
import pandas as pd
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np


class TestDensityTemperature:

    @classmethod
    def setUpClass(self):
        self.h_hub = 100
        self.weather = {'temp_air': pd.Series(data=[267, 268]),
                        'temp_air_2': pd.Series(data=[267, 266]),
                        'pressure': pd.Series(data=[101125, 101000])}
        self.data_height = {'temp_air': 2,
                            'temp_air_2': 10,
                            'pressure': 0}

    def test_temperature_gradient(self):
        # Test pandas.Series
        temp_hub_exp = pd.Series(data=[266.363, 267.36300])
        assert_series_equal(temperature_gradient(self.weather['temp_air'],
                                                 self.data_height['temp_air'],
                                                 self.h_hub),
                            temp_hub_exp)
        # Test numpy array
        assert_array_equal(
            temperature_gradient(np.array(self.weather['temp_air']),
                                 self.data_height['temp_air'],
                                 self.h_hub),
            temp_hub_exp)

    def test_temperature_interpol(self):
        # Test pandas.Series
        temp_hub_exp = pd.Series(data=[267.0, 243.5])
        assert_series_equal(
            temperature_interpol(self.weather['temp_air'],
                                 self.weather['temp_air_2'],
                                 self.data_height['temp_air'],
                                 self.data_height['temp_air_2'],
                                 self.h_hub),
            temp_hub_exp)
        # Test numpy array
        assert_array_equal(
            temperature_interpol(np.array(self.weather['temp_air']),
                                 np.array(self.weather['temp_air_2']),
                                 self.data_height['temp_air'],
                                 self.data_height['temp_air_2'],
                                 self.h_hub),
            temp_hub_exp)

    def test_rho_barometric(self):
        # Test pandas.Series
        rho_exp = pd.Series(data=[1.30305336, 1.29656645])
        assert_series_equal(rho_barometric(self.weather['pressure'],
                                           self.data_height['pressure'],
                                           self.h_hub,
                                           self.weather['temp_air']),
                            rho_exp)
        # Test numpy array
        assert_allclose(rho_barometric(np.array(self.weather['pressure']),
                                       self.data_height['pressure'],
                                       self.h_hub,
                                       np.array(self.weather['temp_air'])),
                        rho_exp)

    def test_rho_ideal_gas(self):
        # Test pandas.Series
        rho_exp = pd.Series(data=[1.30309439, 1.29660728])
        assert_series_equal(rho_ideal_gas(self.weather['pressure'],
                                          self.data_height['pressure'],
                                          self.h_hub,
                                          self.weather['temp_air']),
                            rho_exp)
        # Test numpy array
        assert_allclose(rho_ideal_gas(np.array(self.weather['pressure']),
                                      self.data_height['pressure'],
                                      self.h_hub,
                                      np.array(self.weather['temp_air'])),
                        rho_exp)
