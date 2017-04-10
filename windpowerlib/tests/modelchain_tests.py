import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from nose.tools import eq_


class TestModelchain:

    @classmethod
    def setUpClass(self):
        self.weather = {'temp_air': 267,
                        'temp_air_2': 266,
                        'v_wind': 5.0,
                        'v_wind_2': 4.0,
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

    def test_v_wind_hub(self):
        v_wind_exp = 5.0
        self.data_height['v_wind'] = 100
        eq_(self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        v_wind_exp = 4.0
        self.data_height['v_wind'] = 10
        self.data_height['v_wind_2'] = 100
        eq_(self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        v_wind_exp = 7.7413652271940308
        self.data_height['v_wind_2'] = 8
        eq_(self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

    def test_rho_hub(self):
        rho_exp = 1.303053361499916
        self.data_height['temp_air'] = 100
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

        rho_exp = 1.30795205834766
        self.data_height['temp_air'] = 10
        self.data_height['temp_air_2'] = 100
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

        rho_exp = 1.305914635138703
        self.data_height['temp_air_2'] = 8
        eq_(self.test_mc.rho_hub(self.weather, self.data_height),
            rho_exp)

    def test_run_model_1(self):
        power_output_exp = 724829.76425940311
        test_mc = mc.Modelchain(self.test_wt)
        test_mc.run_model(self.weather, self.data_height)
        eq_(test_mc.power_output, power_output_exp)

    def test_run_model_2(self):
        power_output_exp = 539948.81543840829
        test_mc = mc.Modelchain(self.test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        eq_(test_mc.power_output, power_output_exp)
