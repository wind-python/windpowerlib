import pandas as pd
import numpy as np
import pytest
from pandas.util.testing import assert_frame_equal

from windpowerlib.power_curves import (smooth_power_curve,
                                       wake_losses_to_power_curve)
import windpowerlib.wind_turbine as wt


class TestPowerCurves:

    @classmethod
    def setup_class(self):
        self.test_turbine = {'hub_height': 100,
                             'name': 'E-126/4200',
                             'fetch_curve': 'power_curve'}

    def test_smooth_power_curve(self):
        test_curve = wt.WindTurbine(**self.test_turbine).power_curve
        parameters = {'power_curve_wind_speeds': test_curve['wind_speed'],
                      'power_curve_values': test_curve['value'],
                      'standard_deviation_method': 'turbulence_intensity'}

        # Raise ValueError - `turbulence_intensity` missing
        with pytest.raises(ValueError):
            parameters['standard_deviation_method'] = 'turbulence_intensity'
            smooth_power_curve(**parameters)

        # Test turbulence_intensity method
        parameters['turbulence_intensity'] = 0.5
        wind_speed_values_exp = pd.Series([6.0, 7.0, 8.0, 9.0, 10.0],
                                          name='wind_speed')
        power_values_exp = pd.Series([
            1141906.9806766496, 1577536.8085282773, 1975480.993355767,
            2314059.4022704284, 2590216.6802602503], name='value')
        smoothed_curve_exp = pd.DataFrame(data=pd.concat([
            wind_speed_values_exp, power_values_exp], axis=1))
        smoothed_curve_exp.index = np.arange(5, 10, 1)
        assert_frame_equal(smooth_power_curve(**parameters)[5:10],
                           smoothed_curve_exp)

        # Test Staffel_Pfenninger method
        parameters['standard_deviation_method'] = 'Staffell_Pfenninger'
        power_values_exp = pd.Series([
            929405.1348918702, 1395532.5468724659, 1904826.6851982325,
            2402659.118305521, 2844527.1732449625], name='value')
        smoothed_curve_exp = pd.DataFrame(
            data=pd.concat([wind_speed_values_exp, power_values_exp], axis=1))
        smoothed_curve_exp.index = np.arange(5, 10, 1)
        assert_frame_equal(smooth_power_curve(**parameters)[5:10],
                           smoothed_curve_exp)

        # Raise ValueError - misspelling
        with pytest.raises(ValueError):
            parameters['standard_deviation_method'] = 'misspelled'
            smooth_power_curve(**parameters)

    def test_wake_losses_to_power_curve(self):
        test_curve = wt.WindTurbine(**self.test_turbine).power_curve
        parameters = {'power_curve_wind_speeds': test_curve['wind_speed'],
                      'power_curve_values': test_curve['value'],
                      'wind_farm_efficiency': 0.9}

        # Test constant efficiency
        power_curve_exp = test_curve.copy(deep=True)
        power_curve_exp['value'] = power_curve_exp['value'].values * 0.9
        assert_frame_equal(wake_losses_to_power_curve(**parameters),
                           power_curve_exp)

        # Test efficiency curve
        parameters['wind_farm_efficiency'] = pd.DataFrame(
            pd.concat([pd.Series(np.arange(1, 26, 1)),
                       pd.Series([
                           1.0, 1.0, 1.0, 0.84, 0.85, 0.86, 0.85, 0.85, 0.85,
                           0.86, 0.87, 0.89, 0.92, 0.95, 0.95, 0.96, 0.99,
                           0.95, 0.98, 0.97, 0.99, 1.0, 1.0, 1.0, 1.0])],
                      axis=1))
        parameters['wind_farm_efficiency'].columns = ['wind_speed',
                                                      'efficiency']
        power_curve_exp = test_curve.copy(deep=True)
        power_curve_exp['value'] = (
            power_curve_exp['value'].values * parameters[
                'wind_farm_efficiency']['efficiency'])
        assert_frame_equal(wake_losses_to_power_curve(**parameters),
                           power_curve_exp)

        # Raise TypeError if wind farm efficiency is of wrong type
        with pytest.raises(TypeError):
            parameters['wind_farm_efficiency'] = 1
            wake_losses_to_power_curve(**parameters)


if __name__ == "__main__":
    test = TestPowerCurves()
    test.setup_class()
    test.test_smooth_power_curve()
    test.test_wake_losses_to_power_curve()
