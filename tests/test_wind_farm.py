import pytest
import pandas as pd
import numpy as np
from windpowerlib import WindFarm, WindTurbine
from windpowerlib.tools import WindpowerlibUserWarning


class TestWindFarm:

    @classmethod
    def setup_class(self):
        """Setup default values"""
        self.test_turbine = {'hub_height': 100,
                             'turbine_type': 'E-126/4200'}
        self.test_turbine_2 = {'hub_height': 90,
                               'turbine_type': 'V90/2000',
                               'nominal_power': 2e6}

    def test_initialization_list(self):
        """test simple initialization with wind turbine fleet list"""
        wind_turbine_fleet = [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbines': 3},
            {'wind_turbine': WindTurbine(**self.test_turbine_2),
             'number_of_turbines': 2}]
        windfarm = WindFarm(wind_turbine_fleet=wind_turbine_fleet)
        assert 3 * 4.2e6 + 2 * 2e6 == windfarm.nominal_power

    def test_initialization_list_2(self):
        """test simple initialization with wind turbine fleet list where
        once number of turbines and once total capacity is provided"""
        wind_turbine_fleet = [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbines': 3},
            {'wind_turbine': WindTurbine(**self.test_turbine_2),
             'total_capacity': 2 * 2e6}]
        windfarm = WindFarm(wind_turbine_fleet=wind_turbine_fleet)
        assert 3 * 4.2e6 + 2 * 2e6 == windfarm.nominal_power

    def test_initialization_dataframe(self):
        """test simple initialization with wind turbine fleet dataframe"""
        wind_turbine_fleet = pd.DataFrame(
            data={'wind_turbine': [WindTurbine(**self.test_turbine),
                                   WindTurbine(**self.test_turbine_2)],
                  'number_of_turbines': [3, 2]})
        windfarm = WindFarm(wind_turbine_fleet=wind_turbine_fleet)
        assert 3 * 4.2e6 + 2 * 2e6 == windfarm.nominal_power

    def test_initialization_1(self):
        """test catching error when wind_turbine_fleet not provided as list"""
        msg = 'Wind turbine must be provided as WindTurbine object'
        with pytest.raises(ValueError, match=msg):
            WindFarm(wind_turbine_fleet={'wind_turbine': 'turbine',
                                         'number_of_turbines': 2},
                     name='dummy')

    def test_initialization_2(self):
        """test catching error when WindTurbine in wind_turbine_fleet
        not initialized"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': None,
             'number_of_turbines': 3}]}
        msg = 'Wind turbine must be provided as WindTurbine object'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_3(self):
        """test catching error when wind_turbine not specified in
        wind_turbine_fleet"""
        wind_turbine_fleet = pd.DataFrame(
            data={'wind_turbines': [WindTurbine(**self.test_turbine),
                                   WindTurbine(**self.test_turbine_2)],
                  'number_of_turbines': [3, 2]})
        msg = 'Missing wind_turbine key/column in wind_turbine_fleet'
        with pytest.raises(KeyError, match=msg):
            WindFarm(wind_turbine_fleet=wind_turbine_fleet)

    def test_initialization_4(self, recwarn):
        """test overwriting and raising warning when number_of_turbines and
        total_capacity in wind turbine fleet do not fit"""
        wt1 = WindTurbine(**self.test_turbine)
        wt2 = WindTurbine(**self.test_turbine_2)
        wind_turbine_fleet = pd.DataFrame(
            data={'wind_turbine': [wt1, wt2],
                  'number_of_turbines': [3, 2],
                  'total_capacity': [3, np.nan]},
            index=[0, 1])
        windfarm = WindFarm(wind_turbine_fleet=wind_turbine_fleet)
        total_cap_wt1_expected = \
            wt1.nominal_power * wind_turbine_fleet.loc[0, 'number_of_turbines']
        assert windfarm.wind_turbine_fleet.loc[0, 'total_capacity'] == \
               total_cap_wt1_expected
        total_cap_wt2_expected = \
            wt2.nominal_power * wind_turbine_fleet.loc[1, 'number_of_turbines']
        assert windfarm.wind_turbine_fleet.loc[1, 'total_capacity'] == \
               total_cap_wt2_expected
        assert recwarn.pop(WindpowerlibUserWarning)

    def test_initialization_5(self):
        """test catching error when number of turbines cannot be deduced"""
        wt = WindTurbine(**self.test_turbine)
        wt.nominal_power = None
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': wt,
             'total_capacity': 3e6}]}
        msg = 'Number of turbines of type'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_6(self):
        """test catching error when neither number_of_turbines nor
        total_capacity is provided"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbine': 3e6}]}
        msg = 'Number of turbines of type '
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_7(self):
        """test catching error when total capacity cannot be deduced"""
        wt = WindTurbine(**self.test_turbine)
        wt.nominal_power = None
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': wt,
             'number_of_turbines': 3}]}
        msg = 'Total capacity of turbines of type'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_mean_hub_height(self):
        """tests mean_hub_height method"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbines': 2},
            {'wind_turbine': WindTurbine(**self.test_turbine_2),
             'total_capacity': 3e6}]}
        windfarm = WindFarm(**test_farm)
        assert 97.265 == pytest.approx(
            windfarm.mean_hub_height().hub_height, 1e-3)

    def test_repr(self):
        """Test string representation of WindFarm"""
        test_fleet = [{'wind_turbine': WindTurbine(**self.test_turbine),
                       'number_of_turbines': 2}]
        assert 'E-126/4200' in repr(WindFarm(wind_turbine_fleet=test_fleet))


