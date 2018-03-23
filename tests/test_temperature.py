import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal

from windpowerlib.temperature import linear_gradient


class TestTemperature:

    def test_linear_gradient(self):
        parameters = {'temperature': pd.Series(data=[267, 268]),
                      'temperature_height': 2,
                      'hub_height': 100}

        # Test temperature as pd.Series
        temp_hub_exp = pd.Series(data=[266.363, 267.36300])
        assert_series_equal(linear_gradient(**parameters), temp_hub_exp)

        # Test temperature as np.array
        temp_hub_exp = np.array([266.363, 267.36300])
        parameters['temperature'] = np.array(parameters['temperature'])
        assert_array_equal(linear_gradient(**parameters), temp_hub_exp)
        assert isinstance(linear_gradient(**parameters), np.ndarray)
