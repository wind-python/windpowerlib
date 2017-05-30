import windpowerlib.modelchain as mc
import windpowerlib.wind_turbine as wt
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal, assert_allclose
import pandas as pd
import pytest
import numpy as np


class TestModelChain:

    @classmethod
    def setup_class(self):
        self.test_turbine = {'hub_height': 100,
                             'd_rotor': 80,
                             'turbine_name': 'ENERCON E 126 7500'}

    def test_v_wind_hub(self):
        # Test modelchain with wind_model='logarithmic'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                wind_model='logarithmic')
        # Test modelchain with wind_model='hellman'
        test_mc_2 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  wind_model='hellman')
        weather = {'v_wind': pd.Series(data=[5.0, 6.5]),
                   'v_wind_2': pd.Series(data=[4.0, 5.0]),
                   'z0': 0.15}
        weather_df = pd.DataFrame(data={'v_wind': [5.0, 6.5],
                                        'v_wind_2': [4.0, 5.0],
                                        'z0': 0.15},
                                  index=[0, 1])
        weather_arr = {'v_wind': np.array(weather['v_wind']),
                       'v_wind_2': np.array(weather['v_wind_2']),
                       'z0': 0.15}
        data_height = {'v_wind': 10,
                       'v_wind_2': 8}

        # v_wind is closer to hub height than v_wind_2
        v_wind_exp = pd.Series(data=[7.74137, 10.06377])
        assert_series_equal(test_mc.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([7.74136523, 10.0637748])
        assert_allclose(test_mc.v_wind_hub(weather_arr, data_height),
                        v_wind_exp)
        v_wind_exp = pd.Series(data=[7.12462, 9.26201])
        assert_series_equal(test_mc_2.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc_2.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([7.12462437, 9.26201168])
        assert_allclose(test_mc_2.v_wind_hub(weather_arr, data_height),
                        v_wind_exp)

        # v_wind_2 is closer to hub height than v_wind
        data_height['v_wind'] = 8
        data_height['v_wind_2'] = 10
        v_wind_exp = pd.Series(data=[6.19309, 7.74137])
        assert_series_equal(test_mc.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([6.19309218, 7.74136523])
        assert_allclose(test_mc.v_wind_hub(weather_arr, data_height),
                        v_wind_exp)
        v_wind_exp = pd.Series(data=[5.69970, 7.12462])
        assert_series_equal(test_mc_2.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc_2.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([5.69970, 7.12462437])
        assert_allclose(test_mc_2.v_wind_hub(weather_arr, data_height),
                        v_wind_exp)

        # v_wind is given at hub height
        data_height['v_wind'] = 100
        v_wind_exp = pd.Series(data=[5.0, 6.5])
        assert_series_equal(test_mc.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([5.0, 6.5])
        assert_array_equal(test_mc_2.v_wind_hub(weather_arr, data_height),
                           v_wind_exp)

        # v_wind_2 is given at hub height
        v_wind_exp = pd.Series(data=[4.0, 5.0])
        data_height['v_wind'] = 10
        data_height['v_wind_2'] = 100
        assert_series_equal(test_mc_2.v_wind_hub(weather, data_height),
                            v_wind_exp)
        assert_series_equal(test_mc_2.v_wind_hub(weather_df, data_height),
                            v_wind_exp)
        v_wind_exp = np.array([4.0, 5.0])
        assert_array_equal(test_mc_2.v_wind_hub(weather_arr, data_height),
                           v_wind_exp)

        # v_wind_2 is not in weather
        v_wind_exp = pd.Series(data=[7.12462, 9.26201])
        no_v_wind_2_dict = dict(weather)
        del no_v_wind_2_dict['v_wind_2']
        assert_series_equal(test_mc_2.v_wind_hub(no_v_wind_2_dict,
                                                 data_height),
                            v_wind_exp)
        no_v_wind_2_df = dict(weather_df)
        del no_v_wind_2_df['v_wind_2']
        assert_series_equal(test_mc_2.v_wind_hub(no_v_wind_2_df, data_height),
                            v_wind_exp)

    def test_rho_hub(self):
        # Test modelchain with rho_model='barometric' and
        # temperature_model='gradient'
        test_mc = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                rho_model='barometric',
                                temperature_model='gradient')
        # Test modelchain with rho_model='ideal_gas' and
        # temperature_model='interpolation'
        test_mc_2 = mc.ModelChain(wt.WindTurbine(**self.test_turbine),
                                  rho_model='ideal_gas',
                                  temperature_model='interpolation')
        weather = {'temp_air': pd.Series(data=[267, 268]),
                   'temp_air_2': pd.Series(data=[267, 266]),
                   'pressure': pd.Series(data=[101125, 101000])}
        weather_df = pd.DataFrame(data={'temp_air': [267, 268],
                                        'temp_air_2': [267, 266],
                                        'pressure': [101125, 101000]},
                                  index=[0, 1])
        weather_arr = {'temp_air': np.array(weather['temp_air']),
                       'temp_air_2': np.array(weather['temp_air_2']),
                       'pressure': np.array(weather['pressure'])}
        data_height = {'temp_air': 2,
                       'temp_air_2': 10,
                       'pressure': 0}

        # temp_air_2 is closer to hub height than temp_air
        rho_exp = pd.Series(data=[1.30591, 1.30919])
        assert_series_equal(test_mc.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc.rho_hub(weather_df, data_height), rho_exp)
        rho_exp = np.array([1.30591464, 1.30919432])
        assert_allclose(test_mc.rho_hub(weather_arr, data_height), rho_exp)
        rho_exp = pd.Series(data=[1.30309, 1.42707])
        assert_series_equal(test_mc_2.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc_2.rho_hub(weather_df, data_height),
                            rho_exp)
        rho_exp = np.array([1.30309439, 1.42706674])
        assert_allclose(test_mc_2.rho_hub(weather_arr, data_height), rho_exp)

        # temp_air is closer to hub height than temp_air_2
        data_height['temp_air'] = 10
        data_height['temp_air_2'] = 2
        rho_exp = pd.Series(data=[1.30591, 1.29940])
        assert_series_equal(test_mc.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc.rho_hub(weather_df, data_height), rho_exp)
        rho_exp = np.array([1.30591464, 1.29940284])
        assert_allclose(test_mc.rho_hub(weather_arr, data_height), rho_exp)
        rho_exp = pd.Series(data=[1.30309, 1.19618])
        assert_series_equal(test_mc_2.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc_2.rho_hub(weather_df, data_height),
                            rho_exp)
        rho_exp = np.array([1.30309439, 1.19618159])
        assert_allclose(test_mc_2.rho_hub(weather_arr, data_height), rho_exp)

        # temp_air at hub height
        rho_exp = pd.Series(data=[1.30305, 1.29657])
        data_height['temp_air'] = 100
        assert_series_equal(test_mc.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc.rho_hub(weather_df, data_height), rho_exp)
        rho_exp = np.array([1.30305336, 1.29656645])
        assert_allclose(test_mc.rho_hub(weather_arr, data_height), rho_exp)

        # temp_air_2 at hub height
        rho_exp = pd.Series(data=[1.30309, 1.30636])
        data_height['temp_air'] = 10
        data_height['temp_air_2'] = 100
        assert_series_equal(test_mc_2.rho_hub(weather, data_height), rho_exp)
        assert_series_equal(test_mc_2.rho_hub(weather_df, data_height),
                            rho_exp)
        rho_exp = np.array([1.30309439, 1.30635621])
        assert_allclose(test_mc_2.rho_hub(weather_arr, data_height), rho_exp)

        # temp_air_2 is not in weather
        rho_exp = pd.Series(data=[1.30591, 1.29940])
        no_temp_air_2_dict = dict(weather)
        del no_temp_air_2_dict['temp_air_2']
        assert_series_equal(test_mc.rho_hub(no_temp_air_2_dict, data_height),
                            rho_exp)
        no_temp_air_2_df = dict(weather)
        del no_temp_air_2_df['temp_air_2']
        assert_series_equal(test_mc.rho_hub(no_temp_air_2_df, data_height),
                            rho_exp)

        # Raise KeyError due to missing temp_air_2 while temperature_model =
        # 'interpolation'
        with pytest.raises(KeyError):
            data_height['temp_air_2'] = 100
            no_temp_air_2_dict = dict(weather)
            del no_temp_air_2_dict['temp_air_2']
            test_mc_2.rho_hub(no_temp_air_2_dict, data_height)
        with pytest.raises(KeyError):
            data_height['temp_air_2'] = 100
            no_temp_air_2_df = dict(weather)
            del no_temp_air_2_df['temp_air_2']
            test_mc_2.rho_hub(no_temp_air_2_df, data_height)

    def test_run_model(self):
        weather = {'temp_air': pd.Series(data=[267, 268]),
                   'temp_air_2': pd.Series(data=[267, 266]),
                   'v_wind': pd.Series(data=[5.0, 6.5]),
                   'v_wind_2': pd.Series(data=[4.0, 5.0]),
                   'pressure': pd.Series(data=[101125, 101000]),
                   'z0': 0.15}
        weather_df = pd.DataFrame(data={'v_wind': [5.0, 6.5],
                                        'v_wind_2': [4.0, 5.0],
                                        'z0': 0.15,
                                        'temp_air': [267, 268],
                                        'temp_air_2': [267, 266],
                                        'pressure': [101125, 101000]},
                                  index=[0, 1])
        weather_arr = {'v_wind': np.array(weather['v_wind']),
                       'v_wind_2': np.array(weather['v_wind_2']),
                       'temp_air': np.array(weather['temp_air']),
                       'temp_air_2': np.array(weather['temp_air_2']),
                       'pressure': np.array(weather['pressure']),
                       'z0': np.array([0.15, 0.15])}
        data_height = {'temp_air': 2,
                       'temp_air_2': 10,
                       'v_wind': 10,
                       'v_wind_2': 8,
                       'pressure': 0}
        test_turbine = {'hub_height': 100,
                        'd_rotor': 80,
                        'turbine_name': 'ENERCON E 126 7500',
                        'fetch_curve': 'p'}
        test_modelchain = {'wind_model': 'hellman',
                           'rho_model': 'barometric',
                           'temperature_model': 'interpolation',
                           'power_output_model': 'p_values',
                           'density_corr': True}

        # Test with default parameters of modelchain (p curve)
        power_output_exp = pd.Series(data=[1731887.39768, 3820152.27489],
                                     name='feedin_wind_turbine')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine))
        test_mc.run_model(weather, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with density corrected power curve
        power_output_exp = pd.Series(data=[1430312.76771, 3746075.21279],
                                     name='feedin_wind_turbine')
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test with power coefficient curve
        power_output_exp = pd.Series(data=[557835.45403, 1363746.94496],
                                     name='feedin_wind_turbine')
        test_turbine['fetch_curve'] = 'cp'
        test_modelchain['power_output_model'] = 'cp_values'
        test_modelchain['density_corr'] = False
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Ideal gas equation and density corrected power coefficient curve
        power_output_exp = pd.Series(data=[567683.92454, 1485556.96435],
                                     name='feedin_wind_turbine')
        test_modelchain['rho_model'] = 'ideal_gas'
        test_modelchain['density_corr'] = True
        test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                **test_modelchain)
        test_mc.run_model(weather, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test weather as DataFrame
        test_mc.run_model(weather_df, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Test weather dictionary with numpy.arrays
        power_output_exp = pd.Series(data=[567683.92454, 1485556.96435],
                                     index=[1, 2], name='feedin_wind_turbine')
        test_mc.run_model(weather_arr, data_height)
        assert_series_equal(test_mc.power_output, power_output_exp)

        # Raise ValueErrors due to wrong spelling of parameters
        with pytest.raises(ValueError):
            test_modelchain['power_output_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)
        with pytest.raises(ValueError):
            test_modelchain['power_output_model'] = 'cp_values'
            test_modelchain['wind_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)
        with pytest.raises(ValueError):
            test_modelchain['wind_model'] = 'hellman'
            test_modelchain['rho_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)
        with pytest.raises(ValueError):
            test_modelchain['rho_model'] = 'barometric'
            test_modelchain['temperature_model'] = 'wrong_spelling'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)

        # Raise TypeErrors due to wrong type of `density_corr`
        with pytest.raises(TypeError):
            test_modelchain['temperature_model'] = 'gradient'
            test_modelchain['density_corr'] = 'wrong_type'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)
        with pytest.raises(TypeError):
            test_modelchain['power_output_model'] = 'cp_values'
            test_modelchain['density_corr'] = 'wrong_type'
            test_mc = mc.ModelChain(wt.WindTurbine(**test_turbine),
                                    **test_modelchain)
            test_mc.run_model(weather, data_height)

        # Raise TypeErrors due to missing cp- or p-values
        with pytest.raises(TypeError):
            turbine1 = {'hub_height': 100,
                        'd_rotor': 80,
                        'turbine_name': 'ENERCON E 126 7500',
                        'fetch_curve': 'p'}
            modelchain1 = {'wind_model': 'hellman',
                           'rho_model': 'barometric',
                           'temperature_model': 'interpolation',
                           'power_output_model': 'cp_values',
                           'density_corr': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**turbine1),
                                    **modelchain1)
            test_mc.run_model(weather, data_height)
        with pytest.raises(TypeError):
            turbine2 = {'hub_height': 100,
                        'd_rotor': 80,
                        'turbine_name': 'ENERCON E 126 7500',
                        'fetch_curve': 'cp'}
            modelchain2 = {'wind_model': 'hellman',
                           'rho_model': 'barometric',
                           'temperature_model': 'interpolation',
                           'power_output_model': 'p_values',
                           'density_corr': True}
            test_mc = mc.ModelChain(wt.WindTurbine(**turbine2),
                                    **modelchain2)
            test_mc.run_model(weather, data_height)
