"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
from typing import Dict

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose
from pandas.util.testing import assert_series_equal
from windpowerlib.power_output import (
    power_coefficient_curve,
    power_curve,
    power_curve_density_correction,
)


class TestPowerOutput:
    def setup_class(self):
        self.parameters: Dict = {
            "wind_speed": pd.Series(data=[2.0, 5.5, 7.0]),
            "density": pd.Series(data=[1.3, 1.3, 1.3]),
            "rotor_diameter": 80,
            "power_coefficient_curve_wind_speeds": pd.Series([4.0, 5.0, 6.0]),
            "power_coefficient_curve_values": pd.Series([0.3, 0.4, 0.5]),
        }
        self.parameters2: Dict = {
            "wind_speed": pd.Series(data=[2.0, 5.5, 7.0]),
            "density": pd.Series(data=[1.3, 1.3, 1.3]),
            "density_correction": False,
            "power_curve_wind_speeds": pd.Series([4.0, 5.0, 6.0]),
            "power_curve_values": pd.Series([300, 400, 500]),
        }
        self.power_output_exp1 = pd.Series(
            data=[0.0, 450.0, 0.0], name="feedin_power_plant"
        )
        self.power_output_exp2 = pd.Series(
            data=[0.0, 461.00290572, 0.0], name="feedin_power_plant"
        )

    def test_power_coefficient_curve_1(self):
        """
        Test wind_speed as pd.Series with density and power_coefficient_curve
        as pd.Series and np.array
        """
        power_output_exp = pd.Series(
            data=[0.0, 244615.399, 0.0], name="feedin_power_plant"
        )
        assert_series_equal(
            power_coefficient_curve(**self.parameters), power_output_exp
        )

        parameters = self.parameters
        parameters["density"].to_numpy()
        assert_series_equal(
            power_coefficient_curve(**parameters), power_output_exp
        )

        parameters["power_coefficient_curve_values"] = np.array(
            parameters["power_coefficient_curve_values"]
        )
        parameters["power_coefficient_curve_wind_speeds"] = np.array(
            parameters["power_coefficient_curve_wind_speeds"]
        )
        assert_series_equal(
            power_coefficient_curve(**parameters), power_output_exp
        )

    def test_power_coefficient_curve_output_types(self):
        """
        Test wind_speed as np.array with density and power_coefficient_curve
        as np.array and pd.Series
        """
        assert isinstance(
            power_coefficient_curve(**self.parameters), pd.Series
        )
        self.parameters["wind_speed"] = np.array(self.parameters["wind_speed"])
        assert isinstance(
            power_coefficient_curve(**self.parameters), np.ndarray
        )

    def test_power_coefficient_curve_2(self):
        """TODO: Explain this test"""
        parameters = self.parameters
        power_output_exp = np.array([0.0, 244615.399, 0.0])
        parameters["wind_speed"] = np.array(parameters["wind_speed"])
        assert_allclose(
            power_coefficient_curve(**parameters), power_output_exp
        )
        parameters["density"] = pd.Series(data=parameters["density"])
        assert_allclose(
            power_coefficient_curve(**parameters), power_output_exp
        )
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)
        parameters["power_coefficient_curve_wind_speeds"] = pd.Series(
            data=parameters["power_coefficient_curve_wind_speeds"]
        )
        parameters["power_coefficient_curve_values"] = pd.Series(
            data=parameters["power_coefficient_curve_values"]
        )
        assert_allclose(
            power_coefficient_curve(**parameters), power_output_exp
        )
        assert isinstance(power_coefficient_curve(**parameters), np.ndarray)

    def test_power_curve_1(self):
        # Tests without density correction:
        # Test wind_speed as pd.Series and power_curve as pd.Series and
        # np.array

        assert_series_equal(
            power_curve(**self.parameters2), self.power_output_exp1
        )

    def test_power_curve_2(self):
        """TODO: Explain this test"""
        self.parameters2["power_curve_values"] = np.array(
            self.parameters2["power_curve_values"]
        )
        self.parameters2["power_curve_wind_speeds"] = np.array(
            self.parameters2["power_curve_wind_speeds"]
        )
        assert_series_equal(
            power_curve(**self.parameters2), self.power_output_exp1
        )

    def test_power_curve_3(self):
        """
        Test wind_speed as np.array and power_curve as
        pd.Series and np.array
        """
        power_output_exp = np.array(self.power_output_exp1)
        self.parameters2["wind_speed"] = np.array(
            self.parameters2["wind_speed"]
        )
        assert_allclose(power_curve(**self.parameters2), power_output_exp)
        assert isinstance(power_curve(**self.parameters2), np.ndarray)

    def test_power_curve_4(self):
        """TODO: Explain this test"""
        self.parameters2["power_curve_wind_speeds"] = pd.Series(
            data=self.parameters2["power_curve_wind_speeds"]
        )
        self.parameters2["power_curve_values"] = pd.Series(
            data=self.parameters2["power_curve_values"]
        )
        assert_allclose(
            power_curve(**self.parameters2), self.power_output_exp1
        )
        assert isinstance(power_curve(**self.parameters2), np.ndarray)

    def test_power_curve_5(self):
        """
        Tests with density correction:
        Test wind_speed as np.array with density and power_curve as pd.Series
        and np.array
        """
        power_output_exp = np.array(self.power_output_exp2)
        self.parameters2["density_correction"] = True
        assert_allclose(power_curve(**self.parameters2), power_output_exp)
        assert isinstance(power_curve(**self.parameters2), np.ndarray)

    def test_power_curve_6(self):
        """TODO: Explain this test"""
        self.parameters2["density"] = np.array(self.parameters2["density"])
        assert_allclose(
            power_curve(**self.parameters2), self.power_output_exp2
        )
        assert isinstance(power_curve(**self.parameters2), np.ndarray)

    def test_power_curve_7(self):
        """TODO: Explain this test"""
        self.parameters2["power_curve_values"] = np.array(
            self.parameters2["power_curve_values"]
        )
        self.parameters2["power_curve_wind_speeds"] = np.array(
            self.parameters2["power_curve_wind_speeds"]
        )
        assert_allclose(
            power_curve(**self.parameters2), self.power_output_exp2
        )
        assert isinstance(power_curve(**self.parameters2), np.ndarray)

    def test_power_curve_8(self):
        """
        Test wind_speed as pd.Series with density and power_curve as np. array
         and pd.Series
        """
        self.parameters2["wind_speed"] = pd.Series(
            data=self.parameters2["wind_speed"]
        )
        assert_series_equal(
            power_curve(**self.parameters2), self.power_output_exp2
        )

    def test_power_curve_9(self):
        """TODO: Explain this test"""
        self.parameters2["density"] = pd.Series(
            data=self.parameters2["density"]
        )
        assert_series_equal(
            power_curve(**self.parameters2), self.power_output_exp2
        )

    def test_power_curve_10(self):
        """TODO: Explain this test"""
        self.parameters2["power_curve_wind_speeds"] = pd.Series(
            data=self.parameters2["power_curve_wind_speeds"]
        )
        self.parameters2["power_curve_values"] = pd.Series(
            data=self.parameters2["power_curve_values"]
        )
        assert_series_equal(
            power_curve(**self.parameters2), self.power_output_exp2
        )

    def test_power_curve_11(self):
        """Raise IndexErrors due to wrong type of `density_correction`"""
        with pytest.raises(IndexError, match="too many indices for array"):
            self.parameters2["density"] = "wrong_type"
            power_curve(**self.parameters2)

    def test_power_curve_density_correction(self):
        """TODO: Explain and split this test."""
        parameters = {
            "wind_speed": pd.Series(data=[2.0, 5.5, 7.0]),
            "density": pd.Series(data=[1.3, 1.3, 1.3]),
            "power_curve_wind_speeds": pd.Series([4.0, 5.0, 6.0]),
            "power_curve_values": pd.Series([300, 400, 500]),
        }

        # Test wind_speed as pd.Series with density and power_curve as
        # pd.Series and np.array
        power_output_exp = pd.Series(
            data=[0.0, 461.00290572, 0.0], name="feedin_power_plant"
        )
        assert_series_equal(
            power_curve_density_correction(**parameters), power_output_exp
        )
        parameters["density"] = np.array(parameters["density"])
        assert_series_equal(
            power_curve_density_correction(**parameters), power_output_exp
        )
        parameters["power_curve_values"] = np.array(
            parameters["power_curve_values"]
        )
        parameters["power_curve_wind_speeds"] = np.array(
            parameters["power_curve_wind_speeds"]
        )
        assert_series_equal(
            power_curve_density_correction(**parameters), power_output_exp
        )

        # Test wind_speed as np.array with density and power_curve as np.array
        # and pd.Series
        parameters["wind_speed"] = np.array(parameters["wind_speed"])
        power_output_exp = np.array([0.0, 461.00290572, 0.0])
        assert_allclose(
            power_curve_density_correction(**parameters), power_output_exp
        )
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters["density"] = pd.Series(data=parameters["density"])
        assert_allclose(
            power_curve_density_correction(**parameters), power_output_exp
        )
        assert isinstance(power_curve(**parameters), np.ndarray)
        parameters["power_curve_wind_speeds"] = pd.Series(
            data=parameters["power_curve_wind_speeds"]
        )
        parameters["power_curve_values"] = pd.Series(
            data=parameters["power_curve_values"]
        )
        assert_allclose(
            power_curve_density_correction(**parameters), power_output_exp
        )
        assert isinstance(power_curve(**parameters), np.ndarray)

        # Raise TypeError due to density is None
        with pytest.raises(TypeError):
            parameters["density"] = None
            power_curve_density_correction(**parameters)

    def test_wrong_spelling_density_correction(self):
        parameters = {
            "wind_speed": pd.Series(data=[2.0, 5.5, 7.0]),
            "density": pd.Series(data=[1.3, 1.3, 1.3]),
            "power_curve_wind_speeds": pd.Series([4.0, 5.0, 6.0]),
            "power_curve_values": pd.Series([300, 400, 500]),
        }
        msg = "is an invalid type. `density_correction` must be Boolean"
        with pytest.raises(TypeError, match=msg):
            parameters["density_correction"] = None
            power_curve(**parameters)
