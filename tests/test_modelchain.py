import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal, assert_allclose
import pandas as pd
import pytest
import numpy as np


class TestModelChain:

    @classmethod
    def setup_class(self):
        self.test_turbine = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'turbine_name': 'ENERCON E 126 7500'}

    def test_temperature_hub(self):
        # Test modelchain with temperature_model='linear_gradient'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                temperature_model='linear_gradient')
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
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                density_model='barometric')
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
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                wind_speed_model='logarithmic')
        # Test modelchain with wind_speed_model='hellman'
        test_mc_2 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  wind_speed_model='hellman')
        # Test modelchain with wind_speed_model='interpolation_extrapolation'
        test_mc_3 = mc.ModelChain(
            wt.WindTurbine(**self.test_turbine),
            wind_speed_model='interpolation_extrapolation')

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

        # wind_speed is given at hub height
        weather_df.columns = [np.array(['wind_speed', 'wind_speed',
                                        'roughness_length']),
                              np.array([10, 100, 0])]
        v_wind_exp = pd.Series(data=[5.0, 6.5], name=100)
        assert_series_equal(test_mc.wind_speed_hub(weather_df), v_wind_exp)

    def test_run_model(self):

        temperature_2m = np.array([[267], [268]])
        temperature_10m = np.array([[267], [266]])
        pressure_0m = np.array([[101125], [101000]])
        wind_speed_8m = np.array([[4.0], [5.0]])
        wind_speed_10m = np.array([[5.0], [6.5]])
        roughness_length = np.array([[0.15], [0.15]])
        weather_df = pd.DataFrame(np.hstack((temperature_2m,
                                             temperature_10m,
                                             pressure_0m,
                                             wind_speed_8m,
                                             wind_speed_10m,
                                             roughness_length)),
                                  index=[0, 1],
                                  columns=[np.array(['temperature',
                                                     'temperature',
                                                     'pressure',
                                                     'wind_speed',
                                                     'wind_speed',
                                                     'roughness_length']),
                                           np.array([2, 10, 0, 8, 10, 0])])

        test_turbine = {'hub_height': 100,
                        'rotor_diameter': 80,
                        'turbine_name': 'ENERCON E 126 7500',
                        'fetch_curve': 'power_curve'}

        # Test with default parameters of modelchain (power curve)
        power_output_exp = pd.Series(data=[1731887.39768, 3820152.27489],
                                     name='feedin_wind_turbine')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine))
        test_mc.run_model(weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with density corrected power curve and hellman
        test_modelchain = {'wind_speed_model': 'hellman',
                           'power_output_model': 'power_curve',
                           'density_correction': True}
        power_output_exp = pd.Series(data=[1433937.37959, 3285183.55084],
                                     name='feedin_wind_turbine')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with power coefficient curve and hellman
        power_output_exp = pd.Series(data=[559060.36156, 1251143.98621],
                                     name='feedin_wind_turbine')
        test_turbine['fetch_curve'] = 'power_coefficient_curve'
        test_modelchain = {'wind_speed_model': 'hellman',
                           'power_output_model': 'power_coefficient_curve',
                           'density_correction': False}
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Ideal gas equation and density corrected power coefficient curve
        power_output_exp = pd.Series(data=[569117.952419, 1302746.06501],
                                     name='feedin_wind_turbine')
        test_modelchain = {'wind_speed_model': 'hellman',
                           'density_model': 'ideal_gas',
                           'power_output_model': 'power_coefficient_curve',
                           'density_correction': True}
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather_df)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Raise ValueErrors due to wrong spelling of parameters
        with pytest.raises(ValueError):
            test_modelchain['power_output_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
        with pytest.raises(ValueError):
            test_modelchain['density_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
        with pytest.raises(ValueError):
            test_modelchain['temperature_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
        with pytest.raises(ValueError):
            test_modelchain['wind_speed_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)

        # Raise TypeErrors due to wrong type of `density_correction`
        with pytest.raises(TypeError):
            test_modelchain = {'power_output_model': 'power_curve',
                               'density_correction': 'wrong_type'}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
        with pytest.raises(TypeError):
            test_modelchain = {'power_output_model': 'power_coefficient_curve',
                               'density_correction': 'wrong_type'}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)

        # Raise TypeErrors due to missing cp- or p-values
        with pytest.raises(TypeError):
            test_turbine = {'hub_height': 100,
                            'rotor_diameter': 80,
                            'turbine_name': 'ENERCON E 126 7500',
                            'fetch_curve': 'power_curve'}
            test_modelchain = {'power_output_model': 'power_coefficient_curve',
                               'density_correction': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
        with pytest.raises(TypeError):
            test_turbine = {'hub_height': 100,
                            'rotor_diameter': 80,
                            'turbine_name': 'ENERCON E 126 7500',
                            'fetch_curve': 'power_coefficient_curve'}
            test_modelchain = {'power_output_model': 'power_curve',
                               'density_corr': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather_df)
