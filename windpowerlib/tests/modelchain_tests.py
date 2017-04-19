import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from pandas.util.testing import assert_series_equal
import pandas as pd


class TestModelchain:

    @classmethod
    def setUpClass(self):
        self.weather = {'temp_air': pd.Series(data=[267, 268]),
                        'temp_air_2': pd.Series(data=[267, 266]),
                        'v_wind': pd.Series(data=[5.0, 6.5]),
                        'v_wind_2': pd.Series(data=[4.0, 5.0]),
                        'pressure': pd.Series(data=[101125, 101000]),
                        'z0': 0.15}
        self.weather_df = pd.DataFrame(data={'temp_air': [267, 268],
                                             'temp_air_2': [267, 266],
                                             'v_wind': [5.0, 6.5],
                                             'v_wind_2': [4.0, 5.0],
                                             'pressure': [101125, 101000],
                                             'z0': 0.15},
                                       index=[0, 1])
        self.data_height = {'temp_air': 2,
                            'temp_air_2': 10,
                            'v_wind': 10,
                            'v_wind_2': 8,
                            'pressure': 0}
        self.test_turbine = {'hub_height': 100,
                             'd_rotor': 80,
                             'turbine_name': 'ENERCON E 126 7500',
                             'fetch_curve': 'cp'}
        self.test_wt = wt.WindTurbine(**self.test_turbine)
        self.test_modelchain = {'wind_model': 'hellman',
                                'rho_model': 'barometric',
                                'temperature_model': 'interpolation',
                                'power_output_model': 'cp_values',
                                'density_corr': False}
        self.test_mc = mc.Modelchain(self.test_wt, **self.test_modelchain)

    def test_v_wind_hub(self):
        # v_wind is given at hub height
        v_wind_exp = pd.Series(data=[5.0, 6.5])
        self.data_height['v_wind'] = 100
        assert_series_equal(
            self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        # v_wind_2 is given at hub height
        v_wind_exp = pd.Series(data=[4.0, 5.0])
        self.data_height['v_wind'] = 10
        self.data_height['v_wind_2'] = 100
        assert_series_equal(
            self.test_mc.v_wind_hub(self.weather, self.data_height),
            v_wind_exp)

        # v_wind is closer to hub height than v_wind_2
        v_wind_exp = pd.Series(data=[6.94748, 9.03172])
        self.data_height['v_wind_2'] = 8
        assert_series_equal(self.test_mc.v_wind_hub(self.weather,
                                                    self.data_height),
                            v_wind_exp)

        # Test DataFrame
        assert_series_equal(self.test_mc.v_wind_hub(self.weather_df,
                                                    self.data_height),
                            v_wind_exp)

    def test_rho_hub(self):
        # temp_air at hub height
        rho_exp = pd.Series(data=[1.30305, 1.29657])
        self.data_height['temp_air'] = 100
        assert_series_equal(self.test_mc.rho_hub(self.weather,
                                                 self.data_height), rho_exp)
        # temp_air_2 at hub height
        rho_exp = pd.Series(data=[1.30305, 1.30632])
        self.data_height['temp_air'] = 2
        self.data_height['temp_air_2'] = 100
        assert_series_equal(self.test_mc.rho_hub(self.weather,
                                                 self.data_height), rho_exp)

        rho_exp = pd.Series(data=[1.30305, 1.42702])
        self.data_height['temp_air_2'] = 10
        assert_series_equal(self.test_mc.rho_hub(self.weather,
                                                 self.data_height), rho_exp)
        # Test DataFrame
        assert_series_equal(self.test_mc.rho_hub(self.weather_df,
                                                 self.data_height),
                            rho_exp)

    def test_run_model(self):
        # Test with default parameters of modelchain (cp curve)
        power_output_exp = pd.Series(data=[724829.76425940311, 1605284.00553])
        test_mc = mc.Modelchain(self.test_wt)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_different_models(self):
        # Test density corrected power coefficient curve
        power_output_exp = pd.Series(data=[520383.19719, 1371477.32811])
        self.test_modelchain['density_corr'] = True
        test_wt = wt.WindTurbine(**self.test_turbine)
        test_mc = mc.Modelchain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with power curve
        power_output_exp = pd.Series(data=[1224263.96121, 2733306.74910])
        self.test_turbine['fetch_curve'] = 'P'
        self.test_modelchain['power_output_model'] = 'p_values'
        self.test_modelchain['density_corr'] = False
        test_wt = wt.WindTurbine(**self.test_turbine)
        test_mc = mc.Modelchain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Ideal gas equation and density corrected power curve
        power_output_exp = pd.Series(data=[1310855.11824, 3458801.54045])
        self.test_modelchain['rho_model'] = 'ideal_gas'
        self.test_modelchain['density_corr'] = True
        test_mc = mc.Modelchain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

