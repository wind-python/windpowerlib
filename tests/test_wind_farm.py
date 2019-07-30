import pytest
from windpowerlib import WindFarm, WindTurbine


class TestWindFarm:

    @classmethod
    def setup_class(self):
        """Setup default values"""
        self.test_turbine = {'hub_height': 100,
                             'turbine_type': 'E-126/4200'}
        self.test_turbine_2 = {'hub_height': 90,
                               'turbine_type': 'V90/2000',
                               'nominal_power': 2e6}

    def test_initialization(self):
        """simple initialization"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbines': 3},
            {'wind_turbine': WindTurbine(**self.test_turbine_2),
             'number_of_turbines': 2}]}
        windfarm = WindFarm(**test_farm)
        assert windfarm.nominal_power == 3 * 4.2e6 + 2 * 2e6

    def test_initialization_2(self):
        """WindTurbine in wind_turbine_fleet not initialized"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': None,
             'number_of_turbines': 3}]}
        msg = 'Wind turbine must be provided as WindTurbine object'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_3(self):
        """wind_turbine not specified in wind_turbine_fleet"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbines': None,
             'number_of_turbines': 3}]}
        msg = 'Missing wind_turbine key in wind turbine'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_4(self):
        """deduce number_of_turbines from total_capacity"""
        total_capacity = 3e6
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': WindTurbine(**self.test_turbine_2),
             'total_capacity': total_capacity}]}
        windfarm = WindFarm(**test_farm)
        number_of_turbines = total_capacity / \
                             self.test_turbine_2['nominal_power']
        assert number_of_turbines == windfarm.wind_turbine_fleet[0][
            'number_of_turbines']

    def test_initialization_5(self):
        """deducing number_of_turbines from total_capacity fails"""
        wt = WindTurbine(**self.test_turbine)
        wt.nominal_power = None
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': wt,
             'total_capacity': 3e6}]}
        msg = 'Number of turbines of type'
        with pytest.raises(ValueError, match=msg):
            WindFarm(**test_farm)

    def test_initialization_6(self):
        """number_of_turbines and total_capacity not given"""
        test_farm = {'wind_turbine_fleet': [
            {'wind_turbine': WindTurbine(**self.test_turbine),
             'number_of_turbine': 3e6}]}
        msg = 'Please provide `number_of_turbines` or `total_capacity`'
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

