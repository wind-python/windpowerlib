from pandas.util.testing import assert_series_equal
from windpowerlib.power_output import (cp_curve, cp_curve_density_corr,
                                       p_curve, p_curve_density_corr)
import pandas as pd
import numpy as np
from numpy.testing import assert_allclose


class TestPowerOutput:

    @classmethod
    def setup_class(self):
        self.v_wind = pd.Series(data=[2.0, 5.5, 7.0])
        self.rho_hub = pd.Series(data=[1.3, 1.3, 1.3])
        self.d_rotor = 80
        self.cp_values = pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                      index=[4.0, 5.0, 6.0])
        self.p_values = pd.DataFrame(data={'p': [300, 400, 500]},
                                     index=[4.0, 5.0, 6.0])

    def test_cp_curve(self):
        parameters = {'v_wind': pd.Series(data=[2.0, 5.5, 7.0]),
                      'rho_hub': pd.Series(data=[1.3, 1.3, 1.3]),
                      'd_rotor': 80,
                      'cp_values': pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                                index=[4.0, 5.0, 6.0])}

        # Test v_wind as pd.Series with rho_hub as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 244615.399, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve(**parameters), power_output_exp)
        parameters['rho_hub'] = np.array(parameters['rho_hub'])
        assert_series_equal(cp_curve(**parameters), power_output_exp)

        # Test v_wind as np.array with rho_hub as np.array and pd.Series
        power_output_exp = np.array([0.0, 244615.399, 0.0])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(cp_curve(**parameters), power_output_exp)
        assert isinstance(cp_curve(**parameters), np.ndarray)
        parameters['rho_hub'] = pd.Series(data=parameters['rho_hub'])
        assert_allclose(cp_curve(**parameters), power_output_exp)
        assert isinstance(cp_curve(**parameters), np.ndarray)

    def test_cp_curve_density_corrected(self):
        parameters = {'v_wind': pd.Series(data=[2.0, 5.5, 7.0]),
                      'rho_hub': pd.Series(data=[1.3, 1.3, 1.3]),
                      'd_rotor': 80,
                      'cp_values': pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                                index=[4.0, 5.0, 6.0])}

        # Test v_wind as pd.Series with rho_hub as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 262869.785, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve_density_corr(**parameters),
                            power_output_exp)
        parameters['rho_hub'] = np.array(parameters['rho_hub'])
        assert_series_equal(cp_curve_density_corr(**parameters),
                            power_output_exp)

        # Test v_wind as np.array with rho_hub as np.array and pd.Series
        power_output_exp = np.array([0.0, 262869.785, 0.0])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(cp_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(cp_curve_density_corr(**parameters), np.ndarray)
        parameters['rho_hub'] = pd.Series(data=parameters['rho_hub'])
        assert_allclose(cp_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(cp_curve_density_corr(**parameters), np.ndarray)

    def test_p_curve(self):
        parameters = {'v_wind': pd.Series(data=[2.0, 5.5, 7.0]),
                      'p_values': pd.DataFrame(data={'p': [300, 400, 500]},
                                               index=[4.0, 5.0, 6.0])}

        # Test v_wind as pd.Series
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve(**parameters), power_output_exp)

        # Test v_wind as np.array
        power_output_exp = np.array([0.0, 450.0, 0.0])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(p_curve(**parameters), power_output_exp)
        assert isinstance(p_curve(**parameters), np.ndarray)

    def test_p_curve_density_corrected(self):
        parameters = {'v_wind': pd.Series(data=[2.0, 5.5, 7.0]),
                      'rho_hub': pd.Series(data=[1.3, 1.3, 1.3]),
                      'p_values': pd.DataFrame(data={'p': [300, 400, 500]},
                                               index=[4.0, 5.0, 6.0])}

         # Test v_wind as pd.Series with rho_hub as pd.Series and np.array
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve_density_corr(**parameters),
                            power_output_exp)
        parameters['rho_hub'] = np.array(parameters['rho_hub'])
        assert_series_equal(p_curve_density_corr(**parameters),
                            power_output_exp)

        # Test v_wind as np.array with rho_hub as np.array and pd.Series
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(p_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(p_curve_density_corr(**parameters), np.ndarray)
        parameters['rho_hub'] = pd.Series(data=parameters['rho_hub'])
        assert_allclose(p_curve_density_corr(**parameters),
                        power_output_exp)
        assert isinstance(p_curve_density_corr(**parameters), np.ndarray)
