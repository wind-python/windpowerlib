import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal

import windpowerlib.wind_farm as wf
import windpowerlib.wind_turbine as wt
import windpowerlib.wind_turbine_cluster as wtc
import windpowerlib.turbine_cluster_modelchain as tc_mc


class TestTurbineClusterModelChain:

    @classmethod
    def setup_class(self):
        temperature_2m = np.array([[267], [268]])
        temperature_10m = np.array([[267], [266]])
        pressure_0m = np.array([[101125], [101000]])
        wind_speed_8m = np.array([[4.0], [5.0]])
        wind_speed_10m = np.array([[5.0], [6.5]])
        roughness_length = np.array([[0.15], [0.15]])
        self.weather_df = pd.DataFrame(
                np.hstack((temperature_2m,
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
        self.test_turbine = {'hub_height': 100,
                             'rotor_diameter': 80,
                             'name': 'E-126/4200',
                             'fetch_curve': 'power_curve'}
        self.test_turbine_2 = {'hub_height': 90,
                               'rotor_diameter': 60,
                               'name': 'V90/2000',
                               'fetch_curve': 'power_curve'}
        self.test_farm = {'name': 'test farm',
                          'wind_turbine_fleet': [
                              {'wind_turbine':
                                  wt.WindTurbine(**self.test_turbine),
                               'number_of_turbines': 3}]}
        self.test_farm_2 = {'name': 'test farm',
                            'wind_turbine_fleet':
                                [{'wind_turbine':
                                    wt.WindTurbine(**self.test_turbine),
                                  'number_of_turbines': 3},
                                 {'wind_turbine':
                                     wt.WindTurbine(**self.test_turbine_2),
                                  'number_of_turbines': 3}]}
        self.test_cluster = {'name': 'example_cluster',
                             'wind_farms': [wf.WindFarm(**self.test_farm),
                                            wf.WindFarm(**self.test_farm_2)]}

    def test_run_model(self):
        parameters = {'wake_losses_model': 'dena_mean',
                      'smoothing': False,
                      'standard_deviation_method': 'turbulence_intensity',
                      'smoothing_order': 'wind_farm_power_curves'}

        # Test modelchain with default values
        power_output_exp = pd.Series(data=[4198361.4830405945,
                                           8697966.121234536],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=wf.WindFarm(**self.test_farm), **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test constant efficiency
        parameters['wake_losses_model'] = 'constant_efficiency'
        test_wind_farm = wf.WindFarm(**self.test_farm)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[4420994.806920091,
                                           8516983.651623568],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test smoothing
        parameters['smoothing'] = 'True'
        test_wind_farm = wf.WindFarm(**self.test_farm)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[4581109.03847444,
                                           8145581.914240712],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test wind farm with different turbine types (smoothing)
        test_wind_farm = wf.WindFarm(**self.test_farm_2)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[6777087.9658657005,
                                           12180374.036660176],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test other smoothing order
        parameters['smoothing_order'] = 'turbine_power_curves'
        test_wind_farm = wf.WindFarm(**self.test_farm_2)
        test_wind_farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[6790706.001026006,
                                           12179417.461328149],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_wind_farm, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

    def test_run_model_turbine_cluster(self):
        parameters = {'wake_losses_model': 'dena_mean',
                      'smoothing': False,
                      'standard_deviation_method': 'turbulence_intensity',
                      'smoothing_order': 'wind_farm_power_curves'}

        # Test modelchain with default values
        power_output_exp = pd.Series(data=[10363047.755401008,
                                           21694496.68221325],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=wtc.WindTurbineCluster(**self.test_cluster),
            **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test constant efficiency
        parameters['wake_losses_model'] = 'constant_efficiency'
        test_cluster = wtc.WindTurbineCluster(**self.test_cluster)
        for farm in test_cluster.wind_farms:
            farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[10920128.570572512,
                                           21273144.336885825],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_cluster, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test smoothing
        parameters['smoothing'] = 'True'
        test_cluster = wtc.WindTurbineCluster(**self.test_cluster)
        for farm in test_cluster.wind_farms:
            farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[11360309.77979467,
                                           20328652.64490018],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_cluster, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test wind farm with different turbine types (smoothing)
        test_cluster = wtc.WindTurbineCluster(**self.test_cluster)
        for farm in test_cluster.wind_farms:
            farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[11360309.77979467,
                                           20328652.64490018],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_cluster, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)

        # Test other smoothing order
        parameters['smoothing_order'] = 'turbine_power_curves'
        test_cluster = wtc.WindTurbineCluster(**self.test_cluster)
        for farm in test_cluster.wind_farms:
            farm.efficiency = 0.9
        power_output_exp = pd.Series(data=[11373183.797085874,
                                           20325877.105744187],
                                     name='feedin_power_plant')
        test_tc_mc = tc_mc.TurbineClusterModelChain(
            power_plant=test_cluster, **parameters)
        test_tc_mc.run_model(self.weather_df)
        assert_series_equal(test_tc_mc.power_output, power_output_exp)
