import pytest
import os

from windpowerlib.wind_turbine import (get_turbine_data_from_file, WindTurbine,
                                       get_turbine_types)

class TestWindTurbine:

    def test_error_raising(self):
        source = os.path.join(os.path.dirname(__file__), '../example/data',
                              'example_power_curves.csv')
        self.test_turbine_data = {'hub_height': 100,
                                  'rotor_diameter': 80,
                                  'name': 'turbine_not_in_file',
                                  'fetch_curve': 'power_curve',
                                  'data_source': source}
        # Raise system exit due to turbine type not in file
        with pytest.raises(SystemExit):
            test_turbine = WindTurbine(**self.test_turbine_data)

        # Raise ValueError due to invalid parameter `fetch_curve`
        self.test_turbine_data['fetch_curve'] = 'misspelling'
        self.test_turbine_data['name'] = 'DUMMY 3'
        with pytest.raises(ValueError):
            test_turbine = WindTurbine(**self.test_turbine_data)

        # Raise KeyError due to turbine type not in oedb
        self.test_turbine_data['fetch_curve'] = 'power_curve'
        self.test_turbine_data['data_source'] = 'oedb'
        with pytest.raises(KeyError):
            test_turbine = WindTurbine(**self.test_turbine_data)


    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type='...',
                                       file_='not_existent')

    def test_get_turbine_types(self):
        get_turbine_types(print_out=False)
