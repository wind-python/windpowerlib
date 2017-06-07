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
        # Test pandas.Series
        v_wind_hub_exp = pd.Series(data=[7.74136523, 10.0637748])
        assert_series_equal(logarithmic_wind_profile(**parameters),
                            v_wind_hub_exp)
        # Test numpy array
        parameters['z_0'] = np.array(parameters['z_0'])
        parameters['v_wind'] = np.array(parameters['v_wind'])
        assert_allclose(logarithmic_wind_profile(**parameters), v_wind_hub_exp)
        # Test z_0 is float and obstacle height
        v_wind_hub_exp = np.array([13.54925281, 17.61402865])
        parameters['z_0'] = parameters['z_0'][0]
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
                      'z_0': None,
                      'hellman_exp': None}
        # Test pandas.Series and z_0 is None
        v_wind_hub_exp = pd.Series(data=[6.9474774, 9.03172])
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test z_0 is float
        v_wind_hub_exp = pd.Series(data=[7.12462437, 9.26201168])
        parameters['z_0'] = 0.15
        assert_series_equal(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test array and z_0 is pandas.Series
        parameters['v_wind'] = np.array(parameters['v_wind'])
        parameters['z_0'] = pd.Series(data=[0.15, 0.15])
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test z_0 is array
        parameters['z_0'] = np.array(parameters['z_0'])
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Test hellman_exp is not None
        v_wind_hub_exp = np.array([7.92446596, 10.30180575])
        parameters['hellman_exp'] = 0.2
        assert_allclose(v_wind_hellman(**parameters), v_wind_hub_exp)

        # Raise TypeErrors due to wrong types of `hellman_exp`.
        parameters['hellman_exp'] = 8
        with pytest.raises(TypeError):
            v_wind_hellman(**parameters)
        with pytest.raises(TypeError):
            parameters['hellman_exp'] = False
            v_wind_hellman(**parameters)
