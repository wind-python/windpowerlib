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
        self.h_hub = 100
        self.weather = {'v_wind': 5.0,
                        'z0': 0.15}
        self.data_height = {'v_wind': 10}
        self.test_turbine_1 = {'h_hub': 100,
                               'obstacle_height': 0,
                               'data_height': self.data_height,
                               'weather': self.weather}
        self.test_turbine_2 = {'h_hub': 100,
                               'obstacle_height': 12,
                               'data_height': self.data_height,
                               'weather': self.weather}

    def setup(self):
        self.windturbine = SimpleWindTurbine()

    def test_logarithmic_wind_profile(self):
        v_wind_hub_1_exp = 7.7413652271940308
        v_wind_hub_2_exp = 13.549252811030639
        eq_(logarithmic_wind_profile(**self.test_turbine_1), v_wind_hub_1_exp,
            'Failed to calulate wind speed.')
        eq_(logarithmic_wind_profile(**self.test_turbine_2), v_wind_hub_2_exp,
            'Failed to calulate wind speed.')

    @raises(ValueError)
    def test_raises_value_error(self):
        self.test_turbine_1['obstacle_height'] = 20
        logarithmic_wind_profile(**self.test_turbine_1)
