import pandas as pd
from pandas.util.testing import assert_series_equal
import pytest

from windpowerlib.wind_turbine import read_turbine_data, WindTurbine

class TestWindTurbine:

    def test_error_raising(self):
        self.test_turbine_data = {'hub_height': 100,
                                  'rotor_diameter': 80,
                                  'name': 'turbine_not_in_file',
                                  'fetch_curve': 'power_curve',
                                  'data_source': 'example_power_curves.csv'}
        # Raise system exit
        with pytest.raises(SystemExit):
            test_turbine = WindTurbine(**self.test_turbine_data)

        # Raise ValueError due to invalid parameter `fetch_curve`
        self.test_turbine_data['fetch_curve'] = 'misspelling'
        self.test_turbine_data['name'] = 'DUMMY 3'
        with pytest.raises(ValueError):
            test_turbine = WindTurbine(**self.test_turbine_data)

    def test_read_turbine_data(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            read_turbine_data(filename='not_existent')

