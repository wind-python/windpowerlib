from windpowerlib.wind_speed import logarithmic_wind_profile, v_wind_hellman
import pandas as pd
from pandas.util.testing import assert_series_equal
import numpy as np
from numpy.testing import assert_allclose
import pytest


class TestWindSpeed:

    def test_logarithmic_wind_profile(self):
        parameters = {'v_wind': pd.Series(data=[5.0, 6.5]),
                      'v_wind_height': 10,
                      'hub_height': 100,
                      'z_0': pd.Series(data=[0.15, 0.15]),
                      'obstacle_height': 0}

        # Test v_wind as pd.Series with z_0 as pd.Series, np.array and float
        v_wind_hub_exp = pd.Series(data=[7.74136523, 10.0637748])
        assert_series_equal(logarithmic_wind_profile(**parameters),
                            v_wind_hub_exp)
        parameters['z_0'] = np.array(parameters['z_0'])
        assert_series_equal(logarithmic_wind_profile(**parameters),
                            v_wind_hub_exp)
        parameters['z_0'] = parameters['z_0'][0]
        assert_series_equal(logarithmic_wind_profile(**parameters),
                            v_wind_hub_exp)

        # Test v_wind as np.array with z_0 as float, pd.Series and np.array
        v_wind_hub_exp = np.array([7.74136523, 10.0637748])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(logarithmic_wind_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_wind_profile(**parameters), np.ndarray)
        parameters['z_0'] = pd.Series(data=[parameters['z_0'],
                                      parameters['z_0']])
        assert_allclose(logarithmic_wind_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_wind_profile(**parameters), np.ndarray)
        parameters['z_0'] = np.array(parameters['z_0'])
        assert_allclose(logarithmic_wind_profile(**parameters), v_wind_hub_exp)
        assert isinstance(logarithmic_wind_profile(**parameters), np.ndarray)

        # Test obstacle height is not zero
        v_wind_hub_exp = np.array([13.54925281, 17.61402865])
        parameters['obstacle_height'] = 12
        assert_allclose(logarithmic_wind_profile(**parameters), v_wind_hub_exp)

        # Raise ValueError due to 0.7 * `obstacle_height` > `v_wind_height`
        with pytest.raises(ValueError):
            parameters['obstacle_height'] = 20
            logarithmic_wind_profile(**parameters)

    def test_v_wind_hellman(self):
        parameters = {'v_wind': pd.Series(data=[5.0, 6.5]),
                      'v_wind_height': 10,
                      'hub_height': 100,
                      'z_0': pd.Series(data=[0.15, 0.15]),
                      'hellman_exp': None}

        # Test v_wind is pd.Series with z_0 is pd.Series, np.array and float
        v_wind_hub_exp = pd.Series(data=[7.12462437, 9.26201168])
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)
        parameters['z_0'] = np.array(parameters['z_0'])
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)
        parameters['z_0'] = parameters['z_0'][0]
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test v_wind as np.array with z_0 is float, pd.Series and np.array
        v_wind_hub_exp = np.array([7.12462437, 9.26201168])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)
        assert isinstance(v_wind_hellman(**parameters), np.ndarray)
        parameters['z_0'] = pd.Series(data=(parameters['z_0'],
                                            parameters['z_0']))
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)
        assert isinstance(v_wind_hellman(**parameters), np.ndarray)
        parameters['z_0'] = np.array(parameters['z_0'])
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)
        assert isinstance(v_wind_hellman(**parameters), np.ndarray)

        # Test z_0 is None and hellman_exp is None
        v_wind_hub_exp = pd.Series(data=[6.9474774, 9.03172])
        parameters['v_wind'] = pd.Series(data=parameters['v_wind'])
        parameters['z_0'] = None
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test hellman_exp is not None
        v_wind_hub_exp = pd.Series(data=[7.92446596, 10.30180575])
        parameters['z_0'] = 0.15
        parameters['hellman_exp'] = 0.2
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Raise TypeErrors due to wrong types of `hellman_exp`.
        parameters['hellman_exp'] = 8
        with pytest.raises(TypeError):
            v_wind_hellman(**parameters)
        with pytest.raises(TypeError):
            parameters['hellman_exp'] = False
            v_wind_hellman(**parameters)
