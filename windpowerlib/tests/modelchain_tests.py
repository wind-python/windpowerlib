import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from nose.tools import eq_
from pandas.util.testing import assert_series_equal
import pandas as pd


class TestModelchain:

    @classmethod
    def setUpClass(self):
        self.weather = {'temp_air': 267,
                        'temp_air_2': 266,
                        'v_wind': pd.Series(data=[5.0]),
                        'v_wind_2': pd.Series(data=[4.0]),
                        'pressure': 101125,
                        'z0': 0.15}
        self.data_height = {'temp_air': 2,
                            'temp_air_2': 10,
                            'v_wind': 10,
                            'v_wind_2': 8,
                            'pressure': 0}
        self.test_turbine = {'hub_height': 100,
                             'd_rotor': 80,
                             'turbine_name': 'ENERCON E 126 7500'}
        self.test_wt = wt.WindTurbine(**self.test_turbine)
        self.test_modelchain = {'wind_model': 'hellman',
                                'rho_model': 'barometric',
                                'temperature_model': 'interpolation',
                                'power_output_model': 'cp_values',
                                'density_corr': False}
        self.test_mc = mc.Modelchain(self.test_wt, **self.test_modelchain)

    def test_v_wind_hub(self):
        v_wind_exp = pd.Series(data=[5.0])
        self.data_height['v_wind'] = 100
        assert_series_equal(
            self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        v_wind_exp = pd.Series(data=[4.0])
        self.data_height['v_wind'] = 10
        self.data_height['v_wind_2'] = 100
        assert_series_equal(
            self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        v_wind_exp = pd.Series(data=[6.947477471865689])
        self.data_height['v_wind_2'] = 8
        assert_series_equal(
            self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

    def test_rho_hub(self):
        rho_exp = 1.303053361499916
        self.data_height['temp_air'] = 100
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

        rho_exp = 1.30795205834766
        self.data_height['temp_air'] = 2
        self.data_height['temp_air_2'] = 100
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

        rho_exp = 1.3657124534660552
        self.data_height['temp_air_2'] = 10
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

    def test_run_model_1(self):
        power_output_exp = pd.Series(data=[724829.76425940311])
        test_mc = mc.Modelchain(self.test_wt)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_run_model_2(self):
        power_output_exp = pd.Series(data=[539948.81543840829])
        test_mc = mc.Modelchain(self.test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)
