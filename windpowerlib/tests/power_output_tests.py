from nose.tools import eq_, ok_
from windpowerlib.power_output import cp_curve
import pandas as pd


class Power_Output_Tests:

    @classmethod
    def setUpClass(self):
        self.cp_test = {'v_wind': 5.0,
                        'rho_hub': 1.0,
                        'd_rotor': 80,
                        'cp_series': 0.4}
        self.cp_test_2 = {'v_wind': 5.0,
                          'rho_hub': 1.0,
                          'd_rotor': 80,
                          'cp_series': pd.Series([0.3, 0.4, 0.5])}

    def test_cp_curve(self):
        p_exp = 125663.70614359174
        eq_(cp_curve(**self.cp_test), p_exp)

    def test_cp_curve_series(self):
        ok_(isinstance(cp_curve(**self.cp_test_2), pd.Series))
