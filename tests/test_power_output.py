from pandas.util.testing import assert_series_equal
from windpowerlib.power_output import (power_coefficient_curve,
                                       power_curve, _p_curve_density_corr)
import pandas as pd
import numpy as np
from numpy.testing import assert_allclose
import pytest


class TestPowerOutput:

    def test_power_coefficient_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'rotor_diameter': 80,
                      'cp_values': pd.Series([0.3, 0.4, 0.5],
                                             index=[4.0, 5.0, 6.0])}

        # Tests without density correction:
        # Test wind_speed as pd.Series with density as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 244615.399, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        parameters['density'] = np.array(parameters['density'])
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        # Test wind_speed as np.array with density as np.array and pd.Series
        power_output_exp = np.array([0.0, 244615.399, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)

        # Tests with density correction:
        # Test wind_speed as np.array with density as pd.Series and np.array
        power_output_exp = np.array([0.0, 262869.785, 0.0])
        parameters['density_corr'] = True
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        parameters['density'] = np.array(parameters['density'])
        assert_allclose(power_coefficient_curve(**parameters),
                        power_output_exp)
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        # Test wind_speed as pd.Series with density as np. array and pd.Series
        power_output_exp = pd.Series(data=[0.0, 262869.785, 0.0],
                                     name='feedin_wind_turbine')
        parameters['wind_speed'] = pd.Series(data=parameters['wind_speed'])
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_series_equal(power_coefficient_curve(**parameters),
                            power_output_exp)

        # Raise TypeErrors due to wrong type of `density_corr`
        with pytest.raises(TypeError):
            parameters['density'] = 'wrong_type'
            power_coefficient_curve(**parameters)

    def test_power_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'p_values': pd.Series([300, 400, 500],
                                            index=[4.0, 5.0, 6.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'density_corr': False}

        # Tests without density correction:
        # Test wind_speed as pd.Series
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(power_curve(**parameters), power_output_exp)
        # Test wind_speed as np.array
        power_output_exp = np.array([0.0, 450.0, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)

        # Tests with density correction:
        # Test wind_speed as np.array with density as pd.Series and np.array
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        parameters['density_corr'] = True
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters['density'] = np.array(parameters['density'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)
        # Test wind_speed as pd.Series with density as np. array and pd.Series
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin_wind_turbine')
        parameters['wind_speed'] = pd.Series(data=parameters['wind_speed'])
        assert_series_equal(power_curve(**parameters), power_output_exp)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_series_equal(power_curve(**parameters),
                            power_output_exp)

        # Raise TypeErrors due to wrong type of `density_corr`
        with pytest.raises(TypeError):
            parameters['density'] = 'wrong_type'
            power_curve(**parameters)

    def test_p_curve_density_corrected(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'p_values': pd.Series([300, 400, 500],
                                            index=[4.0, 5.0, 6.0])}

        # Test wind_speed as pd.Series with density as pd.Series and np.array
        power_output_exp = [0.0, 461.00290572240806, 0.0]
        assert _p_curve_density_corr(**parameters) == power_output_exp
        parameters['density'] = np.array(parameters['density'])
        assert _p_curve_density_corr(**parameters) == power_output_exp

        # Test wind_speed as np.array with density as np.array and pd.Series
        assert _p_curve_density_corr(**parameters) == power_output_exp
        parameters['density'] = pd.Series(data=parameters['density'])
        assert _p_curve_density_corr(**parameters) == power_output_exp

        # Raise TypeError due to density is None
        with pytest.raises(TypeError):
            parameters['density'] = None
            _p_curve_density_corr(**parameters)
