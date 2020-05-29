"""
Testing the wind_turbine module.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import os

import pytest

from windpowerlib.tools import WindpowerlibUserWarning
from windpowerlib.wind_turbine import (
    WindTurbine, WindTurbineGroup, get_turbine_data_from_file)


class TestWindTurbine:
    @classmethod
    def setup_class(cls):
        """Setup default values"""
        cls.source = os.path.join(os.path.dirname(__file__), "data")

    def test_warning(self, recwarn):
        test_turbine_data = {
            "hub_height": 100,
            "rotor_diameter": 80,
            "turbine_type": "turbine_not_in_file",
            "path": self.source,
        }
        assert WindTurbine(**test_turbine_data).power_curve is None
        assert recwarn.pop(WindpowerlibUserWarning)

    def test_get_turbine_data_from_file(self):
        # Raise FileNotFoundError due to missing
        with pytest.raises(FileNotFoundError):
            get_turbine_data_from_file(turbine_type="...", path="not_existent")

    @pytest.mark.filterwarnings("ignore:The WindTurbine")
    def test_string_representation_of_wind_turbine(self):
        assert "Wind turbine: ['hub height=120 m'" in repr(WindTurbine(120))

    def test_power_curve_is_of_wrong_type(self):
        """Error raising due to wrong type of WindTurbine.power_curve."""
        test_turbine_data = {
            "hub_height": 100,
            "rotor_diameter": 80,
            "turbine_type": "test_type",
            "power_curve": "string",
        }
        with pytest.raises(TypeError):
            WindTurbine(**test_turbine_data)

    def test_power_coefficient_curve_is_of_wrong_type(self):
        """Error raising due to wrong type of
        WindTurbine.power_coefficient_curve."""
        test_turbine_data = {
            "hub_height": 100,
            "rotor_diameter": 80,
            "turbine_type": "test_type",
            "power_coefficient_curve": "string",
        }
        with pytest.raises(TypeError):
            WindTurbine(**test_turbine_data)

    def test_to_group_method(self):
        example_turbine = {
            "hub_height": 100,
            "rotor_diameter": 70,
            "turbine_type": "DUMMY 3",
            "path": self.source,
        }
        e_t_1 = WindTurbine(**example_turbine)
        assert isinstance(e_t_1.to_group(), WindTurbineGroup)
        assert e_t_1.to_group(5).number_of_turbines == 5
        assert e_t_1.to_group(number_turbines=5).number_of_turbines == 5
        assert e_t_1.to_group(total_capacity=3e6).number_of_turbines == 2.0

    def test_wrongly_defined_to_group_method(self):
        example_turbine = {
            "hub_height": 100,
            "rotor_diameter": 70,
            "turbine_type": "DUMMY 3",
            "path": self.source,
        }
        e_t_1 = WindTurbine(**example_turbine)
        with pytest.raises(
            ValueError,
            match="The 'number' and the 'total_capacity' "
            "parameter are mutually exclusive.",
        ):
            e_t_1.to_group(5, 3000)

    def test_create_unphysical_turbine(self):
        err_msg = "1/2rotor_diameter cannot be greater than hub_height"
        char = {
            "hub_height": 80,
            "rotor_diameter": 160,
            "turbine_type": "DUMMY 3",
            "path": self.source,
        }
        with pytest.raises(ValueError, match=err_msg):
            WindTurbine(**char)
