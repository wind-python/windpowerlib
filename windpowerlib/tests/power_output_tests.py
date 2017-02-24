from nose.tools import ok_
from windpowerlib.power_output import cp_curve
import pandas as pd


class Power_Output_Tests:

    @classmethod
    def setUpClass(self):
        self.cp_test = {'v_wind': [5.0, 6.0, 7.0],
                        'rho_hub': 1.0,
                        'd_rotor': 80,
                        'cp_values': pd.Series(data=[0.3, 0.4, 0.5],
                                               index=[4, 5, 6])}

    def test_cp_curve(self):
        ok_(isinstance(cp_curve(**self.cp_test), pd.Series))
