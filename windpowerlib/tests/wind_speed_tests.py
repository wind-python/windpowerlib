# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 13:03:26 2017

@author: RL-INSTITUT\sabine.haas
"""
import logging
from windpowerlib.wind_speed import logarithmic_wind_profile
from windpowerlib.modelchain import SimpleWindTurbine
from nose.tools import eq_, raises
logging.disable(logging.INFO)


class Wind_speed_Tests:

    @classmethod
    def setUpClass(self):
        self.test_turbine_1 = {'v_wind': 5.0,
                               'z_0': 0.15,
                               'h_hub': 100,
                               'v_wind_height': 10,
                               'obstacle_height': 0}
        self.test_turbine_2 = {'v_wind': 5.0,
                               'z_0': 0.15,
                               'h_hub': 100,
                               'v_wind_height': 10,
                               'obstacle_height': 12}

    def setup(self):
        self.windturbine = SimpleWindTurbine()

    def test_logarithmic_wind_profile(self):
        v_wind_hub_1_exp = 7.7413652271940308
        v_wind_hub_2_exp = 13.549252811030639
        eq_(logarithmic_wind_profile(**self.test_turbine_1), v_wind_hub_1_exp)
        eq_(logarithmic_wind_profile(**self.test_turbine_2), v_wind_hub_2_exp)

    @raises(ValueError)
    def test_raises_value_error(self):
        self.test_turbine_1['obstacle_height'] = 20
        logarithmic_wind_profile(**self.test_turbine_1)
