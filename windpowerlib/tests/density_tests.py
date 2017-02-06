# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 16:00:27 2017

@author: RL-INSTITUT\sabine.haas
"""
import logging
from nose.tools import eq_
from windpowerlib.density import (temperature_gradient, temperature_interpol,
                                  rho_barometric, rho_ideal_gas)
from windpowerlib.modelchain import SimpleWindTurbine
logging.disable(logging.INFO)


class Density_and_Temperature_Tests:

    @classmethod
    def setUpClass(self):
        self.h_hub = 100
        self.weather = {'temp_air': 267,
                        'pressure': 101125}
        self.data_height = {'temp_air': 2,
                            'pressure': 0}
        self.weather_2 = {'temp_air': 266}
        self.data_height_2 = {'temp_air': 10}
        self.test_turbine_1 = {'h_hub': 100,
                               'data_height': self.data_height,
                               'weather': self.weather}
        self.test_turbine_2 = {'h_hub': 100,
                               'data_height': self.data_height,
                               'weather': self.weather,
                               'data_height_2': self.data_height_2,
                               'weather_2': self.weather_2}

    def setup(self):
        self.windturbine = SimpleWindTurbine()

    def test_temperature_gradient(self):
        T_hub_exp = 266.363
        eq_(temperature_gradient(self.weather['temp_air'],
                                 self.data_height['temp_air'],
                                 self.h_hub), T_hub_exp)

    def test_temperature_interpol(self):
        T_hub_exp = 254.75
        eq_(temperature_interpol(
            self.weather['temp_air'], self.weather_2['temp_air'],
            self.data_height['temp_air'], self.data_height_2['temp_air'],
            self.h_hub), T_hub_exp)

    def test_rho_barometric(self):
        rho_exp = 1.303053361499916
        eq_(rho_barometric(self.weather['pressure'],
                           self.data_height['pressure'], self.h_hub, 267.0),
            rho_exp)

    def test_rho_ideal_gas(self):
        rho_exp = 1.3030943935092734
        eq_(rho_ideal_gas(self.weather['pressure'],
                          self.data_height['pressure'], self.h_hub, 267.0),
            rho_exp)
