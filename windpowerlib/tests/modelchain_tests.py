import logging
from windpowerlib import modelchain as mc
from windpowerlib import wind_turbine as wt
from nose.tools import eq_
logging.disable(logging.INFO)


class ModelchainTests:

    @classmethod
    def setUpClass(self):
        self.h_hub = 100
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

        self.coastDat2 = {'pressure': 0,
                          'temp_air': 2,
                          'v_wind': 10,
                          'Z0': 0,
                          'temp_air_2': 10,
                          'v_wind_2': 80}

        self.test_turbine = {'hub_height': 100,
                             'd_rotor': 80,
                             'turbine_name': 'ENERCON E 126 7500'}

        self.test_modelchain = {'wind_model': 'logarithmic',
                                'rho_model': 'barometric',
                                'temperature_model': 'gradient',
                                'power_output_model': 'cp_values',
                                'density_corr': False}

        self.test_modelchain_2 = {'wind_model': 'hellman',
                                  'rho_model': 'barometric',
                                  'temperature_model': 'interpolation',
                                  'power_output_model': 'cp_values',
                                  'density_corr': True}

        self.test_modelchain_3 = {'wind_model': 'logarithmic_closest',
                                  'rho_model': 'ideal_gas',
                                  'temperature_model': 'gradient',
                                  'power_output_model': 'p_values',
                                  'density_corr': False}

        self.test_modelchain_4 = {'wind_model': 'logarithmic',
                                  'rho_model': 'ideal_gas',
                                  'temperature_model': 'interpolation',
                                  'power_output_model': 'p_values',
                                  'density_corr': True}

    def setup(self):
        self.test_wt = wt.WindTurbine(**self.test_turbine)
        self.test_mc = mc.Modelchain(self.test_wt, **self.test_modelchain)
        self.test_mc_2 = mc.Modelchain(self.test_wt, **self.test_modelchain_2)
        self.test_mc_3 = mc.Modelchain(self.test_wt, **self.test_modelchain_3)
        self.test_mc_4 = mc.Modelchain(self.test_wt, **self.test_modelchain_4)

    def test_model_parameters_1(self):
        v_wind_exp = 7.7413652271940308
        eq_(self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)
        rho_exp = 1.3061695788096603
        eq_(self.test_mc.rho_hub(self.weather, self.data_height), rho_exp)
        self.test_mc.run_model(self.coastDat2)

    def test_model_parameters_2(self):
        v_wind_exp = 6.947477471865689
        eq_(self.test_mc_2.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)
        rho_exp = 1.3657124534660552
        eq_(self.test_mc_2.rho_hub(self.weather, self.data_height), rho_exp)
        self.test_mc_2.run_model(self.coastDat2)

    def test_model_parameters_3(self):
        v_wind_exp = 7.7413652271940308
        eq_(self.test_mc_3.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)
        rho_exp = 1.3062107089459725
        eq_(self.test_mc_3.rho_hub(self.weather, self.data_height), rho_exp)
        self.test_mc_3.run_model(self.coastDat2)

    def test_model_parameters_4(self):
        rho_exp = 1.3657554585553522
        eq_(self.test_mc_4.rho_hub(self.weather, self.data_height), rho_exp)
        self.test_mc_4.run_model(self.coastDat2)
