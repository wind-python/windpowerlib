import pandas as pd
import numpy as np
import pytest
from numpy.testing import assert_allclose
from pandas.util.testing import assert_series_equal

from windpowerlib.power_output import (power_coefficient_curve,
                                       power_curve,
                                       power_curve_density_correction)


class TestPowerOutput:

    def test_power_coefficient_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'rotor_diameter': 80,
                      'power_coefficient_curve_wind_speeds':
                          pd.Series([4.0, 5.0, 6.0]),
                      'power_coefficient_curve_values':
                          pd.Series([0.3, 0.4, 0.5])}

        # Test wind_speed as pd.Series with density and power_coefficient_curve
        # as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 244615.399, 0.0],
                                     name='feedin')
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        parameters['density'] = np.array(parameters['density'])
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        parameters['power_coefficient_curve_values'] = np.array(
            parameters['power_coefficient_curve_values'])
        parameters['power_coefficient_curve_wind_speeds'] = np.array(
            parameters['power_coefficient_curve_wind_speeds'])
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        # Test wind_speed as np.array with density and power_coefficient_curve
        # as np.array and pd.Series
        power_output_exp = np.array([0.0, 244615.399, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        parameters['power_coefficient_curve_wind_speeds'] = pd.Series(
            data=parameters['power_coefficient_curve_wind_speeds'])
        parameters['power_coefficient_curve_values'] = pd.Series(
            data=parameters['power_coefficient_curve_values'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)

    def test_power_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'density_correction': False,
                      'power_curve_wind_speeds':
                          pd.Series([4.0, 5.0, 6.0]),
                      'power_curve_values':
                          pd.Series([300, 400, 500])
                      }

        # Tests without density correction:
        # Test wind_speed as pd.Series and power_curve as pd.Series and
        # np.array
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin')
        assert_series_equal(power_curve(**parameters), power_output_exp)
        parameters['power_curve_values'] = np.array(
            parameters['power_curve_values'])
        parameters['power_curve_wind_speeds'] = np.array(
            parameters['power_curve_wind_speeds'])
        assert_series_equal(power_curve(**parameters),
                            power_output_exp)

        # Test wind_speed as np.array and power_curve as pd.Series and np.array
        power_output_exp = np.array([0.0, 450.0, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['power_curve_wind_speeds'] = pd.Series(
            data=parameters['power_curve_wind_speeds'])
        parameters['power_curve_values'] = pd.Series(
            data=parameters['power_curve_values'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)

        # Tests with density correction:
        # Test wind_speed as np.array with density and power_curve as pd.Series
        # and np.array
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        parameters['density_correction'] = True
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['density'] = np.array(parameters['density'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['power_curve_values'] = np.array(
            parameters['power_curve_values'])
        parameters['power_curve_wind_speeds'] = np.array(
            parameters['power_curve_wind_speeds'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)

        # Test wind_speed as pd.Series with density and power_curve as
        # np. array and pd.Series
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin')
        parameters['wind_speed'] = pd.Series(data=parameters['wind_speed'])
        assert_series_equal(power_curve(**parameters), power_output_exp)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_series_equal(power_curve(**parameters),
                            power_output_exp)
        parameters['power_curve_wind_speeds'] = pd.Series(
            data=parameters['power_curve_wind_speeds'])
        parameters['power_curve_values'] = pd.Series(
            data=parameters['power_curve_values'])
        assert_series_equal(power_curve(**parameters),
                            power_output_exp)

        # Raise TypeErrors due to wrong type of `density_correction`
        with pytest.raises(TypeError):
            parameters['density'] = 'wrong_type'
            power_curve(**parameters)

    def test_power_curve_density_correction(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'power_curve_wind_speeds':
                          pd.Series([4.0, 5.0, 6.0]),
                      'power_curve_values':
                          pd.Series([300, 400, 500])
                      }

        # Test wind_speed as pd.Series with density and power_curve as
        # pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin')
        assert_series_equal(power_curve_density_correction(**parameters),
                            power_output_exp)
        parameters['density'] = np.array(parameters['density'])
        assert_series_equal(power_curve_density_correction(**parameters),
                            power_output_exp)
        parameters['power_curve_values'] = np.array(
            parameters['power_curve_values'])
        parameters['power_curve_wind_speeds'] = np.array(
            parameters['power_curve_wind_speeds'])
        assert_series_equal(power_curve_density_correction(**parameters),
                            power_output_exp)

        # Test wind_speed as np.array with density and power_curve as np.array
        # and pd.Series
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        assert_allclose(power_curve_density_correction(**parameters),
                        power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_allclose(power_curve_density_correction(**parameters),
                        power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['power_curve_wind_speeds'] = pd.Series(
            data=parameters['power_curve_wind_speeds'])
        parameters['power_curve_values'] = pd.Series(
            data=parameters['power_curve_values'])
        assert_allclose(power_curve_density_correction(**parameters),
                        power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)

        # Raise TypeError due to density is None
        with pytest.raises(TypeError):
            parameters['density'] = None
            power_curve_density_correction(**parameters)
