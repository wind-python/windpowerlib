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
        # Test pandas.Series
        power_output_exp = pd.Series(data=[0.0, 244615.399, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve(self.v_wind, self.rho_hub, self.d_rotor,
                                     self.cp_values),
                            power_output_exp)
        # Test numpy array
        assert_allclose(cp_curve(np.array(self.v_wind), np.array(self.rho_hub),
                                 self.d_rotor, self.cp_values),
                        power_output_exp)

    def test_cp_curve_density_corrected(self):
        # Test pandas.Series
        power_output_exp = pd.Series(data=[0.0, 262869.785, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve_density_corr(self.v_wind, self.rho_hub,
                                                  self.d_rotor,
                                                  self.cp_values),
                            power_output_exp)
        # Test numpy array
        assert_allclose(cp_curve_density_corr(np.array(self.v_wind),
                                              np.array(self.rho_hub),
                                              self.d_rotor, self.cp_values),
                        power_output_exp)

    def test_p_curve(self):
        # Test pandas.Series
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve(self.v_wind, self.p_values),
                            power_output_exp)
        # Test numpy array
        assert_allclose(p_curve(np.array(self.v_wind), self.p_values),
                        power_output_exp)

    def test_p_curve_density_corrected(self):
        # Test pandas.Series
        power_output_exp = pd.Series(data=[0.0, 461.00290572, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve_density_corr(self.v_wind, self.rho_hub,
                                                 self.p_values),
                            power_output_exp)
        # Test numpy array
        assert_allclose(p_curve_density_corr(np.array(self.v_wind),
                                             np.array(self.rho_hub),
                                             self.p_values),
                        power_output_exp)
