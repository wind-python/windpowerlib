"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal
from numpy.testing import assert_array_equal

from windpowerlib.temperature import linear_gradient


class TestTemperature:

    def test_linear_gradient(self):
        """Test temperature as pd.Series"""
        parameters={'temperature': pd.Series(data=[267, 268]),
                      'temperature_height': 2,
                      'hub_height': 100}
        temp_hub_exp=pd.Series(data=[266.363, 267.36300])
        assert_series_equal(linear_gradient(**parameters), temp_hub_exp)

    def test_temperature_as_np_array(self):
        """Test temperature as np.array"""
        parameters={'temperature': np.array([267, 268]),
                      'temperature_height': 2,
                      'hub_height': 100}
        temp_hub_exp=np.array([266.363, 267.36300])
        assert_array_equal(linear_gradient(**parameters), temp_hub_exp)
        assert isinstance(linear_gradient(**parameters), np.ndarray)
