from windpowerlib.wind_speed import logarithmic_wind_profile, v_wind_hellman
import pandas as pd
from pandas.util.testing import assert_series_equal
import numpy as np
from numpy.testing import assert_allclose
import pytest


class TestWindSpeed:

    @classmethod
    def setup_class(self):
        self.logarithmic = {'v_wind': pd.Series(data=[5.0, 6.5]),
                            'z_0': pd.Series(data=[0.15, 0.15]),
                            'hub_height': 100,
                            'v_wind_height': 10,
                            'obstacle_height': 0}

        self.hellman = {'v_wind': pd.Series(data=[5.0, 6.5]),
                        'hub_height': 100,
                        'v_wind_height': 10,
                        'z_0': None,
                        'hellman_exp': None}

    def test_logarithmic_wind_profile(self):
        # Test pandas.Series
        v_wind_hub_exp = pd.Series(data=[7.74136523, 10.0637748])
        assert_series_equal(logarithmic_wind_profile(**self.logarithmic),
                            v_wind_hub_exp)
        # Test numpy array
        self.logarithmic['z_0'] = np.array(self.logarithmic['z_0'])
        self.logarithmic['v_wind'] = np.array(self.logarithmic['v_wind'])
        assert_allclose(logarithmic_wind_profile(**self.logarithmic),
                        v_wind_hub_exp)
        # Test z_0 is float and obstacle height
        v_wind_hub_exp = np.array([13.54925281, 17.61402865])
        self.logarithmic['z_0'] = self.logarithmic['z_0'][0]
        self.logarithmic['obstacle_height'] = 12
        assert_allclose(logarithmic_wind_profile(**self.logarithmic),
                        v_wind_hub_exp)

    def test_raises_value_error(self):
        r"""
        Raises ValueError due to 0.7 * `obstacle_height` > `v_wind_height`.

        """
        with pytest.raises(ValueError):
            logarithmic_wind_profile(v_wind=5.5, v_wind_height=10,
                                     hub_height=100, z_0=0.15,
                                     obstacle_height=20)

    def test_v_wind_hellman(self):
        # Test pandas.Series and z_0 is None
        v_wind_hub_exp = pd.Series(data=[6.9474774, 9.03172])
        assert_series_equal(v_wind_hellman(**self.hellman), v_wind_hub_exp)

        # Test z_0 is float
        v_wind_hub_exp = pd.Series(data=[7.12462437, 9.26201168])
        self.hellman['z_0'] = 0.15
        assert_series_equal(v_wind_hellman(**self.hellman), v_wind_hub_exp)

        # Test array and z_0 is pandas.Series
        self.hellman['v_wind'] = np.array(self.hellman['v_wind'])
        self.hellman['z_0'] = pd.Series(data=[0.15, 0.15])
        assert_allclose(v_wind_hellman(**self.hellman), v_wind_hub_exp)

        # Test z_0 is array
        self.hellman['z_0'] = np.array(self.hellman['z_0'])
        assert_allclose(v_wind_hellman(**self.hellman), v_wind_hub_exp)

        # Test hellman_exp is not None
        v_wind_hub_exp = np.array([7.92446596, 10.30180575])
        self.hellman['hellman_exp'] = 0.2
        assert_allclose(v_wind_hellman(**self.hellman), v_wind_hub_exp)

    def test_raises_type_error(self):
        r"""
        Test TypeError for wrong types of `hellman_exp`.

        """
        with pytest.raises(TypeError):
            v_wind_hellman(v_wind=5.5, v_wind_height=10, hub_height=100,
                           hellman_exp=8)
        with pytest.raises(TypeError):
            v_wind_hellman(v_wind=5.5, v_wind_height=10, hub_height=100,
                           hellman_exp=False)
