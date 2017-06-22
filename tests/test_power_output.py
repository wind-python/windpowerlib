from pandas.util.testing import assert_series_equal
from windpowerlib.power_output import (power_coefficient_curve,
                                       cp_curve_density_corr,
                                       power_curve, p_curve_density_corr)
import pandas as pd
import numpy as np
from numpy.testing import assert_allclose


class TestPowerOutput:

    def test_power_coefficient_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'rotor_diameter': 80,
                      'cp_values': pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                                index=[4.0, 5.0, 6.0])}

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

    def test_cp_curve_density_corrected(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'rotor_diameter': 80,
                      'cp_values': pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                                index=[4.0, 5.0, 6.0])}

        # Test wind_speed as pd.Series with density as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 262869.785, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve_density_corr(**parameters),
                            power_output_exp)
        parameters['density'] = np.array(parameters['density'])
        assert_series_equal(cp_curve_density_corr(**parameters),
                            power_output_exp)

        # Test wind_speed as np.array with density as np.array and pd.Series
        power_output_exp = np.array([0.0, 262869.785, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(cp_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(cp_curve_density_corr(**parameters), np.ndarray)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_allclose(cp_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(cp_curve_density_corr(**parameters), np.ndarray)

    def test_power_curve(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'p_values': pd.DataFrame(data={'p': [300, 400, 500]},
                                               index=[4.0, 5.0, 6.0])}

        # Test wind_speed as pd.Series
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(power_curve(**parameters), power_output_exp)

        # Test wind_speed as np.array
        power_output_exp = np.array([0.0, 450.0, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(power_curve(**parameters), power_output_exp)
        assert isinstance(power_curve(**parameters), np.ndarray)

    def test_p_curve_density_corrected(self):
        parameters = {'wind_speed': pd.Series(data=[2.0, 5.5, 7.0]),
                      'density': pd.Series(data=[1.3, 1.3, 1.3]),
                      'p_values': pd.DataFrame(data={'p': [300, 400, 500]},
                                               index=[4.0, 5.0, 6.0])}

        # Test wind_speed as pd.Series with density as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve_density_corr(**parameters),
                            power_output_exp)
        parameters['density'] = np.array(parameters['density'])
        assert_series_equal(p_curve_density_corr(**parameters),
                            power_output_exp)

        # Test wind_speed as np.array with density as np.array and pd.Series
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        parameters['wind_speed'] = np.array(parameters['wind_speed'])
        assert_allclose(p_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(p_curve_density_corr(**parameters), np.ndarray)
        parameters['density'] = pd.Series(data=parameters['density'])
        assert_allclose(p_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(p_curve_density_corr(**parameters), np.ndarray)
