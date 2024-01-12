"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import os
from example import modelchain_example as mc_e
from example import turbine_cluster_modelchain_example as tc_mc_e
from numpy.testing import assert_allclose
import pytest_notebook


class TestExamples:
    def test_modelchain_example_flh(self):
        # tests full load hours
        weather = mc_e.get_weather_data("weather.csv")
        my_turbine, e126, dummy_turbine = mc_e.initialize_wind_turbines()
        mc_e.calculate_power_output(weather, my_turbine, e126, dummy_turbine)

        assert_allclose(
            2730.142, (e126.power_output.sum() / e126.nominal_power), 0.01
        )
        assert_allclose(
            1882.7567,
            (my_turbine.power_output.sum() / my_turbine.nominal_power),
            0.01,
        )

    def test_turbine_cluster_modelchain_example_flh(self):
        # tests full load hours
        weather = mc_e.get_weather_data("weather.csv")
        my_turbine, e126, dummy_turbine = mc_e.initialize_wind_turbines()
        example_farm, example_farm_2 = tc_mc_e.initialize_wind_farms(
            my_turbine, e126
        )
        example_cluster = tc_mc_e.initialize_wind_turbine_cluster(
            example_farm, example_farm_2
        )
        tc_mc_e.calculate_power_output(weather, example_farm, example_cluster)
        assert_allclose(
            2004.84125,
            (example_farm.power_output.sum() / example_farm.nominal_power),
            0.01,
        )
        assert_allclose(
            2156.794154,
            (
                example_cluster.power_output.sum()
                / example_cluster.nominal_power
            ),
            0.01,
        )

    def _notebook_run(self, path):
        """
        Execute a notebook and collect output.
        Returns execution errors.
        """
        notebook = pytest_notebook.notebook.load_notebook(path=path)
        result = pytest_notebook.execution.execute_notebook(
            notebook,
            with_coverage=False,
            timeout=600,
        )
        return result.exec_error

    def test_modelchain_example_ipynb(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        errors = self._notebook_run(
            os.path.join(dir_path, "modelchain_example.ipynb")
        )
        assert errors is None

    def test_turbine_cluster_modelchain_example_ipynb(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        errors = self._notebook_run(
            os.path.join(dir_path, "turbine_cluster_modelchain_example.ipynb")
        )
        assert errors is None
