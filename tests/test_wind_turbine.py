import pytest
import os

from windpowerlib.wind_turbine import (get_turbine_data_from_file, WindTurbine,
                                       get_turbine_types)


class TestWindTurbine:

    def test_initialization_power_curve(self):

        # power curve from oedb turbine data
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': True,
                                  'turbine_type': 'E-126/4200'}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # power curve from self provided csv file
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': 'example_power_curves.csv',
                                  'turbine_type': 'DUMMY 3',
                                  'path': '../example/data'}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power curve
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': {'wind_speed': [0, 10],
                                                  'value': [0, 3]}}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

    def test_initialization_power_coefficient_curve(self):

        # power coefficient curve from oedb turbine data
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve': True,
                                  'turbine_type': 'E-126/4200'}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # power coefficient curve from self provided csv file
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve':
                                      'example_power_curves.csv',
                                  'turbine_type': 'DUMMY 3',
                                  'path': '../example/data'}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power coefficient curve
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve':
                                      {'wind_speed': [0, 10],
                                       'value': [0, 3]}}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

    def test_error_raising(self):

        # Raise KeyError due to turbine type not in oedb turbine data
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': True,
                                  'turbine_type': 'E-turbine_not_in_file/4200'}
        with pytest.raises(KeyError):
            WindTurbine(**self.test_turbine_data)

        # Raise KeyError due to turbine type not in file
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': True,
                                  'turbine_type': 'turbine_not_in_file',
                                  'power_coefficient_curve':
                                      'example_power_curves.csv',
                                  'path': '../example/data'}
        with pytest.raises(KeyError):
            WindTurbine(**self.test_turbine_data)

        # Raise TypeError due to invalid type for power curve and power
        # coefficient curve
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': 3.0}
        with pytest.raises(TypeError):
            WindTurbine(**self.test_turbine_data)

        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve': 3.0}
        with pytest.raises(TypeError):
            WindTurbine(**self.test_turbine_data)

        # Raise AttributeError in case no power or power coefficient curve
        # is set
        self.test_turbine_data = {'hub_height': 100}
        with pytest.raises(AttributeError):
            WindTurbine(**self.test_turbine_data)

    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type='...',
                                       file_='not_existent')

    def test_get_turbine_types(self):
        get_turbine_types(print_out=True, filter_=True)
        get_turbine_types(print_out=False, filter_=False)
