"""
SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""

import os
import subprocess
import tempfile
import nbformat
import sys
from example import modelchain_example as mc_e
from example import turbine_cluster_modelchain_example as tc_mc_e
from numpy.testing import assert_allclose
import pytest


class TestExamples:

    def test_modelchain_example_flh(self):
        # tests full load hours
        weather = mc_e.get_weather_data('weather.csv')
        my_turbine, e126, dummy_turbine = mc_e.initialize_wind_turbines()
        mc_e.calculate_power_output(weather, my_turbine, e126, dummy_turbine)

        assert_allclose(2764.194772, (e126.power_output.sum() /
                                      e126.nominal_power), 0.01)
        assert_allclose(1882.7567, (my_turbine.power_output.sum() /
                                    my_turbine.nominal_power), 0.01)

    def test_turbine_cluster_modelchain_example_flh(self):
        # tests full load hours
        weather = mc_e.get_weather_data('weather.csv')
        my_turbine, e126, dummy_turbine = mc_e.initialize_wind_turbines()
        example_farm, example_farm_2 = tc_mc_e.initialize_wind_farms(
            my_turbine, e126)
        example_cluster = tc_mc_e.initialize_wind_turbine_cluster(
            example_farm, example_farm_2)
        tc_mc_e.calculate_power_output(weather, example_farm, example_cluster)
        assert_allclose(1956.164053, (example_farm.power_output.sum() /
                                      example_farm.nominal_power), 0.01)
        assert_allclose(2156.794154, (example_cluster.power_output.sum() /
                                      example_cluster.nominal_power), 0.01)

    def _notebook_run(self, path):
        """
        Execute a notebook via nbconvert and collect output.
        Returns (parsed nb object, execution errors)
        """
        dirname, __ = os.path.split(path)
        os.chdir(dirname)
        with tempfile.NamedTemporaryFile(suffix=".ipynb") as fout:
            args = ["jupyter", "nbconvert", "--to", "notebook", "--execute",
                    "--ExecutePreprocessor.timeout=60",
                    "--output", fout.name, path]
            subprocess.check_call(args)

            fout.seek(0)
            nb = nbformat.read(fout, nbformat.current_nbformat)

        errors = [output for cell in nb.cells if "outputs" in cell
                  for output in cell["outputs"]
                  if output.output_type == "error"]

        return nb, errors

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6")
    def test_modelchain_example_ipynb(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        nb, errors = self._notebook_run(
            os.path.join(dir_path, 'modelchain_example.ipynb'))
        assert errors == []

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6")
    def test_turbine_cluster_modelchain_example_ipynb(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        nb, errors = self._notebook_run(
            os.path.join(dir_path, 'turbine_cluster_modelchain_example.ipynb'))
        assert errors == []
