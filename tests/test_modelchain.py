import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from pandas.util.testing import assert_series_equal
import pandas as pd
import pytest


class TestModelChain:

    @classmethod
    def setup_class(self):
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
                             'fetch_curve': 'P'}
        self.test_wt = wt.WindTurbine(**self.test_turbine)
        self.test_modelchain = {'wind_model': 'hellman',
                                'rho_model': 'barometric',
                                'temperature_model': 'interpolation',
                                'power_output_model': 'p_values',
                                'density_corr': False}
        self.test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)

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
        v_wind_exp = pd.Series(data=[7.12462, 9.26201])
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
        # Test with default parameters of modelchain (p curve)
        power_output_exp = pd.Series(data=[1731887.39768, 3820152.27489],
                                     name='feedin_wind_turbine')
        test_mc = mc.ModelChain(self.test_wt)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_different_models(self):
        # Test density corrected power curve
        power_output_exp = pd.Series(data=[1430312.76771, 3746075.21279],
                                     name='feedin_wind_turbine')
        self.test_modelchain['density_corr'] = True
        test_wt = wt.WindTurbine(**self.test_turbine)
        test_mc = mc.ModelChain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with power coefficient curve
        power_output_exp = pd.Series(data=[557835.45403, 1363746.94496],
                                     name='feedin_wind_turbine')
        self.test_turbine['fetch_curve'] = 'cp'
        self.test_modelchain['power_output_model'] = 'cp_values'
        self.test_modelchain['density_corr'] = False
        test_wt = wt.WindTurbine(**self.test_turbine)
        test_mc = mc.ModelChain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Ideal gas equation and density corrected power coefficient curve
        power_output_exp = pd.Series(data=[567683.92454, 1485556.96435],
                                     name='feedin_wind_turbine')
        self.test_modelchain['rho_model'] = 'ideal_gas'
        self.test_modelchain['density_corr'] = True
        test_mc = mc.ModelChain(test_wt, **self.test_modelchain)
        test_mc.run_model(self.weather, self.data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

    def test_raises_value_error(self):
        r"""
        Raises ValueError due to wrong spelling of the parameters `rho_model`,
        `power_output_model`, `wind_model` and `temperature_model`.

        """
        with pytest.raises(ValueError):
            self.test_modelchain['power_output_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)
            test_mc.run_model(self.weather, self.data_height)
        with pytest.raises(ValueError):
            self.test_modelchain['power_output_model'] = 'cp_values'
            self.test_modelchain['wind_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)
            test_mc.run_model(self.weather, self.data_height)
        with pytest.raises(ValueError):
            self.test_modelchain['wind_model'] = 'hellman'
            self.test_modelchain['rho_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)
            test_mc.run_model(self.weather, self.data_height)
        with pytest.raises(ValueError):
            self.test_modelchain['rho_model'] = 'barometric'
            self.test_modelchain['temperature_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)
            test_mc.run_model(self.weather, self.data_height)
# TODO: pytest.raises(ExpectedException, func, *args, **kwargs)
    def test_raises_type_error(self):
        r"""
        Raises TypeError due to wrong type of `density_corr`.

        """
        with pytest.raises(TypeError):
            self.test_modelchain['temperature_model'] = 'gradient'
            self.test_modelchain['density_corr'] = 'wrong_type'
            test_mc = mc.ModelChain(self.test_wt, **self.test_modelchain)
            test_mc.run_model(self.weather, self.data_height)
        with pytest.raises(TypeError):
                self.test_modelchain['power_output_model'] = 'p_values'
                self.test_turbine['fetch_curve'] = 'cp'
                test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                        **self.test_modelchain)
                test_mc.run_model(self.weather, self.data_height)








