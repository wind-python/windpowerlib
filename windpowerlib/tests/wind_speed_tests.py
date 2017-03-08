from windpowerlib.wind_speed import logarithmic_wind_profile, v_wind_hellman
from nose.tools import eq_, raises
import pandas as pd


class Wind_speed_Tests:

    @classmethod
    def setUpClass(self):
        self.logarithmic_test = {'v_wind': 5.0,
                                 'z_0': 0.15,
                                 'hub_height': 100,
                                 'v_wind_height': 10,
                                 'obstacle_height': 0}

        self.logarithmic_test_2 = {'v_wind': pd.Series(data=[5.0, 6.5]),
                                   'z_0': 0.15,
                                   'hub_height': 100,
                                   'v_wind_height': 10,
                                   'obstacle_height': 0}

        self.hellman_test = {'v_wind': 5.0,
                             'hub_height': 100,
                             'v_wind_height': 10}

        self.hellman_test_2 = {'v_wind': 5.0,
                               'hub_height': 100,
                               'v_wind_height': 10,
                               'z_0': 0.15}

    def test_logarithmic_wind_profile(self):
        v_wind_hub_exp = 7.7413652271940308
        eq_(logarithmic_wind_profile(**self.logarithmic_test),
            v_wind_hub_exp)

    def test_logarithmic_wind_profile_obstacles(self):
        v_wind_hub_exp = 13.549252811030639
        self.logarithmic_test['obstacle_height'] = 12
        eq_(logarithmic_wind_profile(**self.logarithmic_test),
            v_wind_hub_exp)

    def test_logarithmic_wind_profile_series(self):
        v_wind_hub_exp = pd.Series(data=[7.7413652271940308,
                                         10.06377479535224])
        eq_(all(logarithmic_wind_profile(**self.logarithmic_test_2)),
            all(v_wind_hub_exp))

    @raises(ValueError)
    def test_raises_value_error(self):
        r"""
        Raises ValueError if 0.7 * obstacle height is higher than hub height.

        """
        self.logarithmic_test['obstacle_height'] = 20
        logarithmic_wind_profile(**self.logarithmic_test)

    def test_v_wind_hellman(self):
        v_wind_hub_exp = 6.947477471865689
        eq_(v_wind_hellman(**self.hellman_test), v_wind_hub_exp)

    def test_v_wind_hellman_with_z0(self):
        v_wind_hub_exp = 7.1246243695751321
        eq_(v_wind_hellman(**self.hellman_test_2), v_wind_hub_exp)

    def test_v_wind_hellman_with_exp(self):
        v_wind_hub_exp = 7.924465962305568
        eq_(v_wind_hellman(hellman_exp=0.2, **self.hellman_test_2),
            v_wind_hub_exp)
