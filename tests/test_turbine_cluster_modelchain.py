import pandas as pd
import numpy as np
import pytest
from pandas.util.testing import assert_series_equal

import windpowerlib.wind_farm as wf
import windpowerlib.wind_turbine as wt
import windpowerlib.turbine_cluster_modelchain as tc_mc


class TestTurbineClusterModelChain:

    @classmethod
    def setup_class(self):
        self.test_turbine = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'name': 'ENERCON E 126 7500',
                             'fetch_curve': 'power_curve'}
        self.test_farm = {'name': 'test farm',
                          'wind_turbine_fleet': [
                              {'wind_turbine':
                                   wt.WindTurbine(**self.test_turbine),
                               'number_of_turbines': 3}]}

    def test_run_model(self):
        parameters = {'wake_losses_model': 'dena_mean',
                      'smoothing': False,
                      'standard_deviation_method': 'turbulence_intensity',
                      'smoothing_order': 'wind_farm_power_curves'}
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

        # Test modelchain with default values
        power_output_exp = pd.Series(data=[4409211.803349806,
                                           10212484.219845157],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=wf.WindFarm(**self.test_farm), **parameters)
        test_tc_mc.run_model(weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test constant efficiency
        parameters['wake_losses_model'] = 'constant_efficiency'
        test_wind_farm = wf.WindFarm(**self.test_farm)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[4676095.973725522,
                                           10314411.142196147],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # TODO: Test power efficiency curve?

        # Test smoothing
        parameters['smoothing'] = 'True'
        test_wind_farm = wf.WindFarm(**self.test_farm)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[5015168.554748144,
                                           10389592.995632712],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test other smoothing order # TODO: Test different wind turbines
        parameters['smoothing_order'] = 'turbine_power_curves'
        test_wind_farm = wf.WindFarm(**self.test_farm)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[5015168.554748144,
                                           10389592.995632712],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)


        # TODO: test turbine cluster