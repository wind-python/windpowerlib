from pandas.util.testing import assert_series_equal
from windpowerlib.power_output import (cp_curve, cp_curve_density_corr,
                                       p_curve, p_curve_density_corr)
import pandas as pd


class PowerOutputTests:

    @classmethod
    def setUpClass(self):
        self.v_wind = pd.Series(data=[2.0, 5.5, 7.0])
        self.rho_hub = pd.Series(data=[1.3, 1.3, 1.3])
        self.d_rotor = 80
        self.cp_values = pd.DataFrame(data={'cp': [0.3, 0.4, 0.5]},
                                      index=[4.0, 5.0, 6.0])
        self.p_values = pd.DataFrame(data={'P': [300, 400, 500]},
                                     index=[4.0, 5.0, 6.0])

    def test_cp_curve(self):
        power_output_exp = pd.Series(data=[0.0, 244615.399, 0.0])
        assert_series_equal(cp_curve(self.v_wind, self.rho_hub, self.d_rotor,
                                     self.cp_values),
                            power_output_exp)

    def test_cp_curve_density_corrected(self):
        power_output_exp = pd.Series(data=[0.0, 262869.785, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(cp_curve_density_corr(self.v_wind, self.rho_hub,
                                                  self.d_rotor,
                                                  self.cp_values),
                            power_output_exp)

    def test_p_curve(self):
        power_output_exp = pd.Series(data=[0.0, 450.0, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve(self.p_values, self.v_wind),
                            power_output_exp)

    def test_p_curve_density_corrected(self):
        power_output_exp = pd.Series(data=[0.0, 461.002, 0.0],
                                     name='feedin_wind_turbine')
        assert_series_equal(p_curve_density_corr(self.v_wind, self.rho_hub,
                                                 self.p_values),
                            power_output_exp)
