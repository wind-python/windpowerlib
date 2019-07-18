import pytest
import pandas as pd
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
        self.test_turbine_data = {
            'hub_height': 100,
            'power_curve': 'example_power_curves.csv',
            'turbine_type': 'DUMMY 3',
            'path': os.path.join(os.path.dirname(__file__), '../example/data')}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power curve (dictionary)
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': {'wind_speed': [0, 10],
                                                  'value': [0, 3]}}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power curve (dataframe)
        self.test_turbine_data = {
            'hub_height': 100,
            'power_curve': pd.DataFrame({'wind_speed': [0, 10],
                                         'value': [0, 3]})}
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
        self.test_turbine_data = {
            'hub_height': 100,
            'power_coefficient_curve': 'example_power_curves.csv',
            'nominal_power': 'example_turbine_data.csv',
            'turbine_type': 'DUMMY 3',
            'path': os.path.join(os.path.dirname(__file__), '../example/data')}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power coefficient curve (dictionary)
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve':
                                      {'wind_speed': [0, 10],
                                       'value': [0, 0.3]},
                                  'nominal_power': 3e6}
        try:
            WindTurbine(**self.test_turbine_data)
            assert True
        except:
            assert False

        # directly provided power coefficient curve (dataframe)
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve':
                                      pd.DataFrame({
                                          'wind_speed': [0, 10],
                                          'value': [0, 3]}),
                                  'nominal_power': 3e6}
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
        self.test_turbine_data = {
            'hub_height': 100,
            'power_curve': True,
            'turbine_type': 'turbine_not_in_file',
            'power_coefficient_curve': 'example_power_curves.csv',
            'path': os.path.join(os.path.dirname(__file__), '../example/data')}
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

        # Raise TypeError due to invalid type for nominal power
        self.test_turbine_data = {'hub_height': 100,
                                  'power_curve': True,
                                  'turbine_type': 'E-126/4200',
                                  'nominal_power': [3]}
        with pytest.raises(TypeError):
            WindTurbine(**self.test_turbine_data)

        # Raise AttributeError in case no power or power coefficient curve
        # is set
        self.test_turbine_data = {'hub_height': 100}
        with pytest.raises(AttributeError):
            WindTurbine(**self.test_turbine_data)

        # Raise ValueError due to missing nominal power when using power
        # coefficient curve
        self.test_turbine_data = {'hub_height': 100,
                                  'power_coefficient_curve':
                                      pd.DataFrame({
                                          'wind_speed': [0, 10],
                                          'value': [0, 3]})}
        with pytest.raises(ValueError):
            WindTurbine(**self.test_turbine_data)

    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type='...',
                                       file_='not_existent')

    def test_get_turbine_types(self):
        # local with and without filter
        get_turbine_types(turbine_library='local', print_out=True,
                          filter_=True)
        get_turbine_types(turbine_library='local', print_out=False,
                          filter_=False)
        # oedb with and without filter
        get_turbine_types(turbine_library='oedb', print_out=False,
                          filter_=True)
        get_turbine_types(turbine_library='oedb', print_out=False,
                          filter_=False)
