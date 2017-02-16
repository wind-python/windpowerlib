# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 13:10:09 2017

@author: RL-INSTITUT\sabine.haas
"""
from nose.tools import eq_, raises, ok_
from windpowerlib.power_output import (tpo_through_cp, tpo_through_P,
                                       interpolate_P_curve)
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

    def test_tpo_through_cp(self):
        p_exp = 125663.70614359174
        eq_(tpo_through_cp(**self.cp_test), p_exp)

    def test_tpo_through_cp_series(self):
        ok_(isinstance(tpo_through_cp(**self.cp_test_2), pd.Series))














 