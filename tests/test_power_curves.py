import pandas as pd
import numpy as np
import pytest
from pandas.util.testing import  assert_frame_equal

from windpowerlib.power_curves import smooth_power_curve, wake_losses_to_power_curve
import windpowerlib.wind_turbine as wt

class TestPowerCurves:

    def test_smooth_power_curve(self):
        self.test_turbine = {'hub_height': 100,
                             'name': 'ENERCON E 126 7500',
                             'fetch_curve': 'power_curve'}
        test_curve = wt.WindTurbine(**self.test_turbine).power_curve
        parameters = {'power_curve_wind_speeds': test_curve['wind_speed'], 'power_curve_values': test_curve['power'],
                      'standard_deviation_method': 'turbulence_intensity'}

        # Raise ValueError - `turbulence_intensity` missing
        with pytest.raises(ValueError):
            parameters['standard_deviation_method'] = 'turbulence_intensity'
            smooth_power_curve(**parameters)

        # Test turbulence_intensity method
        parameters['turbulence_intensity'] = 0.5
        wind_speed_values_exp = pd.Series([
            0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0,
            19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5,
            31.0, 31.5, 32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5, 37.0, 37.5, 38.0, 38.5, 39.0, 39.5,
            40.0, 40.5], name='wind_speed')
        power_values_exp = pd.Series([
            0.00000000e+00, 1.29408532e+02, 2.74537745e+04, 1.40329364e+05, 3.81419979e+05, 7.79535308e+05,
            1.32843968e+06, 1.97212403e+06, 2.63632973e+06, 3.26229343e+06, 3.81677075e+06, 4.27224440e+06,
            4.61366043e+06, 4.83323795e+06, 4.93460775e+06, 4.93159174e+06, 4.84407865e+06, 4.69360159e+06,
            4.50002765e+06, 4.27955843e+06, 4.04440559e+06, 3.80280303e+06, 3.55991998e+06, 3.31829062e+06,
            3.07856896e+06, 2.83995558e+06, 2.72036897e+06, 2.60052999e+06, 2.48050066e+06, 2.36108653e+06,
            2.24229318e+06, 2.12469193e+06, 2.00824913e+06, 1.89389472e+06, 1.78155356e+06, 1.67173211e+06,
            1.56433223e+06, 1.46003624e+06, 1.35872165e+06, 1.26054125e+06, 1.16536872e+06, 1.07339238e+06,
            9.84482922e+05, 8.98515461e+05, 8.15369663e+05, 7.34929771e+05, 6.57084612e+05, 5.81727543e+05,
            5.08756385e+05, 4.38073320e+05, 3.69584779e+05, 3.03201313e+05, 2.38837454e+05, 1.76411574e+05,
            1.15845735e+05, 5.70655434e+04, 0.00000000e+00], name='power')
        smoothed_curve_exp = pd.DataFrame(data=pd.concat([wind_speed_values_exp, power_values_exp], axis=1))
        assert_frame_equal(smooth_power_curve(**parameters), smoothed_curve_exp)
        # Test Staffel_Pfenninger method
        parameters['standard_deviation_method'] = 'Staffell_Pfenninger'
        power_values_exp = pd.Series([
            1.622617624147696, 2046.0790594164896, 27453.77446698656, 110797.97957354058, 283160.33899177634,
            569897.5962815176, 991242.9728229153, 1557220.5881869125, 2251719.594235872, 3026232.4980683727,
            3815395.4208982917, 4559077.054622287, 5216030.835333325, 5766491.4918826725, 6206745.153382668,
            6539199.922991546, 6762561.3266230915, 6867856.564678423, 6842759.478226526, 6680474.614754306,
            6386743.355370536, 5981168.352724711, 5493368.359927479, 4956804.542587387, 4403075.69268235,
            3858130.00551364, 3595063.4934183094, 3340640.9697569, 3096127.02360098, 2862525.3109403835,
            2640396.750509171, 2430122.0448174304, 2231742.4070679806, 2045310.6869086046, 1870526.2443415099,
            1707112.9695448321, 1554567.6486531352, 1412544.1278254208, 1280443.9792064743, 1157734.4493543901,
            1043792.3491461624, 938109.6060543727, 840084.3465088347, 749136.1522378596, 664710.6144769953,
            586282.3766447674, 513356.9551039379, 445471.58855416544, 382195.32945327926, 323128.55669016804,
            267902.0580718591, 216175.80422289658, 167637.51216986368, 122001.07699036643, 79004.93315009678,
            38410.393198714024, 0.0], name='power')
        smoothed_curve_exp = pd.DataFrame(data=pd.concat([wind_speed_values_exp, power_values_exp], axis=1))
        assert_frame_equal(smooth_power_curve(**parameters), smoothed_curve_exp)

        # Raise ValueError - misspelling
        with pytest.raises(ValueError):
            parameters['standard_deviation_method'] = 'misspelled'
            smooth_power_curve(**parameters)

    def test_wake_losses_to_power_curve(self):
        self.test_turbine = {'hub_height': 100,
                             'name': 'ENERCON E 126 7500',
                             'fetch_curve': 'power_curve'}
        test_curve = wt.WindTurbine(**self.test_turbine).power_curve
        parameters = {'power_curve_wind_speeds': test_curve['wind_speed'], 'power_curve_values': test_curve['power'],
                      'wind_farm_efficiency': 0.9, 'wake_losses_model': 'constant_efficiency'}

        # Test constant efficiency
        power_curve_exp = test_curve.copy(deep=True)
        power_curve_exp['power'] = power_curve_exp['power'].values * 0.9
        assert_frame_equal(wake_losses_to_power_curve(**parameters), power_curve_exp)

        # Raise TypeError if wind farm efficiency is not float
        with pytest.raises(TypeError):
            parameters['wind_farm_efficiency'] = 1
            wake_losses_to_power_curve(**parameters)

        # Test efficiency curve
        parameters['wake_losses_model'] = 'power_efficiency_curve'
        parameters['wind_farm_efficiency'] = pd.DataFrame(
            pd.concat([pd.Series(np.arange(0, 27, 1)),
                       pd.Series([1.0, 1.0, 1.0, 0.84, 0.85, 0.86, 0.85, 0.85, 0.85, 0.86, 0.87, 0.89, 0.92, 0.95, 0.95,
                                  0.96, 0.99, 0.95, 0.98, 0.97, 0.99, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])], axis=1))
        parameters['wind_farm_efficiency'].columns = ['wind_speed', 'efficiency']
        power_curve_exp = test_curve.copy(deep=True)
        power_curve_exp['power'] = power_curve_exp['power'].values * parameters['wind_farm_efficiency']['efficiency']
        assert_frame_equal(wake_losses_to_power_curve(**parameters), power_curve_exp)

        # Raise TypeError if efficiency is not DataFrame
        with pytest.raises(TypeError):
            parameters['wind_farm_efficiency'] = pd.Series([1, 2, 3])
            wake_losses_to_power_curve(**parameters)

        # Raise ValueError - misspelling
        with pytest.raises(ValueError):
            parameters['wake_losses_model'] = 'misspelled'
            wake_losses_to_power_curve(**parameters)

