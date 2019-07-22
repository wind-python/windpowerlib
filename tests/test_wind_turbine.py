import pytest
import os

from windpowerlib.wind_turbine import (get_turbine_data_from_file, WindTurbine,
                                       get_turbine_types)


class TestWindTurbine:

    def test_error_raising(self):
        source = os.path.join(os.path.dirname(__file__), '../example/data')
        self.test_turbine_data = {'hub_height': 100,
                                  'rotor_diameter': 80,
                                  'turbine_type': 'turbine_not_in_file',
                                  'path': source}
        # Raise system exit due to turbine type not in file
        # with pytest.raises(SystemExit):
        assert(WindTurbine(**self.test_turbine_data).power_curve is None)

    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type='...',
                                       path='not_existent')

    def test_get_turbine_types(self):
        get_turbine_types(print_out=True, filter_=True)
        get_turbine_types(print_out=False, filter_=False)
