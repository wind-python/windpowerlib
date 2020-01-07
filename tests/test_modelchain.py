"""
Testing the ``modelchain`` module.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import pandas as pd
import numpy as np
import pytest
from pandas.util.testing import assert_series_equal

import windpowerlib.wind_turbine as wt
import windpowerlib.modelchain as mc


class TestModelChain:

    @classmethod
    def setup_class(self):
        """Setup default values"""
        self.test_turbine = {'hub_height': 100,
                             'turbine_type': 'E-126/4200',
                             'power_curve': pd.DataFrame(
                                 data={'value': [0.0, 4200 * 1000],
                                       'wind_speed': [0.0, 25.0]})}

        temperature_2m = np.array([[267], [268]])
        temperature_10m = np.array([[267], [266]])
        pressure_0m = np.array([[101125], [101000]])
        wind_speed_8m = np.array([[4.0], [5.0]])
        wind_speed_10m = np.array([[5.0], [6.5]])
        roughness_length = np.array([[0.15], [0.15]])
        self.weather_df = pd.DataFrame(
            np.hstack((temperature_2m, temperature_10m, pressure_0m,
                       wind_speed_8m, wind_speed_10m, roughness_length)),
            index=[0, 1],
            columns=[np.array(['temperature', 'temperature', 'pressure',
                               'wind_speed', 'wind_speed',
                               'roughness_length']),
                     np.array([2, 10, 0, 8, 10, 0])])

    def test_temperature_hub(self):
        # Test modelchain with temperature_model='linear_gradient'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine))
        # Test modelchain with temperature_model='interpolation_extrapolation'
        test_mc_2 = mc.ModelChain(
            wt.WindTurbine(**self.test_turbine),
            temperature_model='interpolation_extrapolation')

        # Parameters for tests
        temperature_2m = np.array([[267], [268]])
        temperature_10m = np.array([[267], [266]])
        weather_df = pd.DataFrame(np.hstack((temperature_2m,
                                             temperature_10m)),
                                  index=[0, 1],
                                  columns=[np.array(['temperature',
                                                     'temperature']),
                                           np.array([2, 10])])

        # temperature_10m is closer to hub height than temperature_2m
        temp_exp = pd.Series(data=[266.415, 265.415], name=10)
        assert_series_equal(test_mc.temperature_hub(weather_df), temp_exp)
        temp_exp = pd.Series(data=[267.0, 243.5])
        assert_series_equal(test_mc_2.temperature_hub(weather_df), temp_exp)

        # change heights of temperatures so that old temperature_2m is now used
        weather_df.columns = [np.array(['temperature', 'temperature']),
                              np.array([10, 200])]
        temp_exp = pd.Series(data=[266.415, 267.415], name=10)
        assert_series_equal(test_mc.temperature_hub(weather_df), temp_exp)
        temp_exp = pd.Series(data=[267.0, 267.052632])
        assert_series_equal(test_mc_2.temperature_hub(weather_df), temp_exp)

        # temperature at hub height
        weather_df.columns = [np.array(['temperature', 'temperature']),
                              np.array([100, 10])]
        temp_exp = pd.Series(data=[267, 268], name=100)
        assert_series_equal(test_mc.temperature_hub(weather_df), temp_exp)

    def test_density_hub(self):
        # Test modelchain with density_model='barometric'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine))
        # Test modelchain with density_model='ideal_gas'
        test_mc_2 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  density_model='ideal_gas')
        # Test modelchain with density_model='interpolation_extrapolation'
        test_mc_3 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  density_model='interpolation_extrapolation')

        # Parameters for tests
        temperature_2m = np.array([[267], [268]])
        temperature_10m = np.array([[267], [266]])
        pressure_0m = np.array([[101125], [101000]])
        weather_df = pd.DataFrame(np.hstack((temperature_2m,
                                             temperature_10m,
                                             pressure_0m)),
                                  index=[0, 1],
                                  columns=[np.array(['temperature',
                                                     'temperature',
                                                     'pressure']),
                                           np.array([2, 10, 0])])

        # temperature_10m is closer to hub height than temperature_2m
        rho_exp = pd.Series(data=[1.30591, 1.30919])
        assert_series_equal(test_mc.density_hub(weather_df), rho_exp)
        rho_exp = pd.Series(data=[1.30595575725, 1.30923554056])
        assert_series_equal(test_mc_2.density_hub(weather_df), rho_exp)

        # change heights of temperatures so that old temperature_2m is now used
        weather_df.columns = [np.array(['temperature', 'temperature',
                                        'pressure']),
                              np.array([10, 200, 0])]
        rho_exp = pd.Series(data=[1.30591, 1.29940])
        assert_series_equal(test_mc.density_hub(weather_df), rho_exp)
        rho_exp = pd.Series(data=[1.30595575725, 1.29944375221])
        assert_series_equal(test_mc_2.density_hub(weather_df), rho_exp)

        # temperature at hub height
        weather_df.columns = [np.array(['temperature', 'temperature',
                                        'pressure']),
                              np.array([100, 10, 0])]
        rho_exp = pd.Series(data=[1.30305, 1.29657])
        assert_series_equal(test_mc.density_hub(weather_df), rho_exp)

        # density interpolation
        density_10m = np.array([[1.30591], [1.29940]])
        density_150m = np.array([[1.30305], [1.29657]])
        weather_df = pd.DataFrame(np.hstack((density_10m,
                                             density_150m)),
                                  index=[0, 1],
                                  columns=[np.array(['density',
                                                     'density']),
                                           np.array([10, 150])])
        rho_exp = pd.Series(data=[1.304071, 1.297581])
        assert_series_equal(test_mc_3.density_hub(weather_df), rho_exp)

    def test_wind_speed_hub(self):
        # Test modelchain with wind_speed_model='logarithmic'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine))
        # Test modelchain with wind_speed_model='hellman'
        test_mc_2 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  wind_speed_model='hellman')
        # Test modelchain with wind_speed_model='interpolation_extrapolation'
        test_mc_3 = mc.ModelChain(
            wt.WindTurbine(**self.test_turbine),
            wind_speed_model='interpolation_extrapolation')
        # Test modelchain with
        # wind_speed_model='log_interpolation_extrapolation'
        test_mc_4 = mc.ModelChain(
            wt.WindTurbine(**self.test_turbine),
            wind_speed_model='log_interpolation_extrapolation')

        # Parameters for tests
        wind_speed_8m = np.array([[4.0], [5.0]])
        wind_speed_10m = np.array([[5.0], [6.5]])
        roughness_length = np.array([[0.15], [0.15]])
        weather_df = pd.DataFrame(np.hstack((wind_speed_8m,
                                             wind_speed_10m,
                                             roughness_length)),
                                  index=[0, 1],
                                  columns=[np.array(['wind_speed',
                                                     'wind_speed',
                                                     'roughness_length']),
                                           np.array([8, 10, 0])])

        # wind_speed_10m is closer to hub height than wind_speed_8m
        v_wind_exp = pd.Series(data=[7.74137, 10.06377])
        assert_series_equal(test_mc.wind_speed_hub(weather_df), v_wind_exp)
        v_wind_exp = pd.Series(data=[7.12462, 9.26201])
        assert_series_equal(test_mc_2.wind_speed_hub(weather_df), v_wind_exp)
        v_wind_exp = pd.Series(data=[50.0, 74.0])
        assert_series_equal(test_mc_3.wind_speed_hub(weather_df), v_wind_exp)
        v_wind_exp = pd.Series(data=[15.3188511585, 21.9782767378])
        assert_series_equal(test_mc_4.wind_speed_hub(weather_df), v_wind_exp)

        # wind_speed is given at hub height
        weather_df.columns = [np.array(['wind_speed', 'wind_speed',
                                        'roughness_length']),
                              np.array([10, 100, 0])]
        v_wind_exp = pd.Series(data=[5.0, 6.5], name=100)
        assert_series_equal(test_mc.wind_speed_hub(weather_df), v_wind_exp)

    # ***** test_run_model *********

    def test_with_default_parameter(self):
        """Test with default parameters of modelchain (power curve)"""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4200'}
        power_output_exp = pd.Series(data=[1637405.4840444783,
                                           3154438.3894902095],
                                     name='feedin_power_plant')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine))
        test_mc.run_model(self.weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_with_density_corrected_power_curve_and_hellman(self):
        """Test with density corrected power curve and hellman"""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4200'}
        test_modelchain = {'wind_speed_model': 'hellman',
                           'power_output_model': 'power_curve',
                           'density_correction': True}
        power_output_exp = pd.Series(data=[1366958.544547462,
                                           2823402.837201821],
                                     name='feedin_power_plant')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(self.weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_with_power_coefficient_curve_and_hellman(self):
        """Test with power coefficient curve and hellman"""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4200'}
        power_output_exp = pd.Series(data=[534137.5112701517,
                                           1103611.1736067757],
                                     name='feedin_power_plant')
        test_modelchain = {'wind_speed_model': 'hellman',
                           'power_output_model': 'power_coefficient_curve',
                           'density_correction': False}
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(self.weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_wrong_spelling_power_output_model(self):
        """Raise ValueErrors due to wrong spelling of power_output_model"""
        with pytest.raises(ValueError):
            test_modelchain = {'wind_speed_model': 'hellman',
                               'power_output_model': 'wrong_spelling',
                               'density_correction': False}
            test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    def test_wrong_spelling_density_model(self):
        """Raise ValueErrors due to wrong spelling of density_model"""
        with pytest.raises(ValueError):
            test_modelchain = {'wind_speed_model': 'hellman',
                               'power_output_model': 'power_coefficient_curve',
                               'density_correction': False,
                               'density_model': 'wrong_spelling'}
            test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    def test_wrong_spelling_temperature_model(self):
        """Raise ValueErrors due to wrong spelling of temperature_model"""
        with pytest.raises(ValueError):
            test_modelchain = {'wind_speed_model': 'hellman',
                               'power_output_model': 'power_coefficient_curve',
                               'density_correction': False,
                               'temperature_model': 'wrong_spelling'}
            test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    def test_wrong_spelling_wind_speed_model(self):
        """Raise ValueErrors due to wrong spelling of wind_speed_model"""
        with pytest.raises(ValueError):
            test_modelchain = {'wind_speed_model': 'wrong_spelling',
                               'power_output_model': 'power_coefficient_curve',
                               'density_correction': False}
            test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    def test_wrong_density_correction_type(self):
        """Raise TypeErrors due to wrong type of `density_correction`"""
        with pytest.raises(TypeError):
            test_modelchain = {'power_output_model': 'power_curve',
                               'density_correction': 'wrong_type'}
            test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    @pytest.mark.filterwarnings("ignore:The WindTurbine")
    def test_missing_cp_values(self):
        """Raise TypeErrors due to missing cp-values"""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4201'}
        msg = "Power coefficient curve values of"
        with pytest.raises(TypeError, match=msg):
            test_modelchain = {'power_output_model': 'power_coefficient_curve',
                               'density_correction': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    @pytest.mark.filterwarnings("ignore:The WindTurbine")
    def test_missing_p_values(self):
        """Raise TypeErrors due to missing p-values"""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4205'}
        msg = "Power curve values of"
        with pytest.raises(TypeError, match=msg):
            test_modelchain = {'power_output_model': 'power_curve',
                               'density_corr': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(self.weather_df)

    def test_modelchain_with_power_curve_as_dict(self):
        """Test power curves as dict"""
        my_turbine = {'nominal_power': 3e6, 'hub_height': 105,
                      'rotor_diameter': 70,
                      'power_curve': {
                          'value': [p * 1000 for p in [
                              0.0, 26.0, 180.0, 1500.0, 3000.0, 3000.0]],
                          'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]},
                      'power_coefficient_curve': {
                          'value': [0.0, 0.43, 0.45, 0.35, 0.12, 0.03],
                          'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]}}
        power_output_exp = pd.Series(data=[919055.54840,
                                           1541786.60559],
                                     name='feedin_power_plant')
        test_mc = mc.ModelChain(wt.WindTurbine(**my_turbine))
        test_mc.run_model(self.weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_modelchain_with_power_coefficient_curve_as_dict(self):
        """Test power coefficient curves as dict"""
        my_turbine = {'nominal_power': 3e6, 'hub_height': 105,
                      'rotor_diameter': 70,
                      'power_curve': {
                          'value': [p * 1000 for p in [
                              0.0, 26.0, 180.0, 1500.0, 3000.0, 3000.0]],
                          'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]},
                      'power_coefficient_curve': {
                          'value': [0.0, 0.43, 0.45, 0.35, 0.12, 0.03],
                          'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]}}
        power_output_exp = pd.Series(data=[469518.35104,
                                           901794.28532],
                                     name='feedin_power_plant')
        test_mc = mc.ModelChain(wt.WindTurbine(**my_turbine),
                                power_output_model='power_coefficient_curve')
        test_mc.run_model(self.weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_heigths_as_string(self):
        """Test run_model if data heights are of type string."""
        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_type': 'E-126/4200'}

        # Convert data heights to str
        string_weather = self.weather_df.copy()
        string_weather.columns = pd.MultiIndex.from_arrays([
            string_weather.columns.get_level_values(0),
            string_weather.columns.get_level_values(1).astype(str)])

        # Heights in the original DataFrame are of type np.int64
        assert isinstance(self.weather_df.columns.get_level_values(1)[0],
                          np.int64)
        assert isinstance(string_weather.columns.get_level_values(1)[0], str)

        test_modelchain = {'power_output_model': 'power_curve',
                           'density_corr': True}
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(string_weather)
