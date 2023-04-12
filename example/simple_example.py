"""
The ``turbine_cluster_modelchain_example`` module shows how to calculate the
power output of wind farms and wind turbine clusters with the windpowerlib.
A cluster can be useful if you want to calculate the feed-in of a region for
which you want to use one single weather data point.

Functions that are used in the ``modelchain_example``, like the initialization
of wind turbines, are imported and used without further explanations.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import pandas as pd
import requests
import os

from windpowerlib import WindFarm
from windpowerlib import WindTurbine
from windpowerlib import TurbineClusterModelChain
from windpowerlib import WindTurbineCluster

# You can use the logging package to get logging messages from the windpowerlib
# Change the logging level if you want more or less messages
import logging

logging.getLogger().setLevel(logging.INFO)


def get_weather_data(filename="weather.csv", **kwargs):
    r"""
    Imports weather data from a file.

    The data include wind speed at two different heights in m/s, air
    temperature in two different heights in K, surface roughness length in m
    and air pressure in Pa. The height in m for which the data applies is
    specified in the second row.
    In case no weather data file exists, an example weather data file is
    automatically downloaded and stored in the same directory as this example.

    Parameters
    ----------
    filename : str
        Filename of the weather data file. Default: 'weather.csv'.

    Other Parameters
    ----------------
    datapath : str, optional
        Path where the weather data file is stored.
        Default is the same directory this example is stored in.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        DataFrame with time series for wind speed `wind_speed` in m/s,
        temperature `temperature` in K, roughness length `roughness_length`
        in m, and pressure `pressure` in Pa.
        The columns of the DataFrame are a MultiIndex where the first level
        contains the variable name as string (e.g. 'wind_speed') and the
        second level contains the height as integer at which it applies
        (e.g. 10, if it was measured at a height of 10 m). The index is a
        DateTimeIndex.

    """

    if "datapath" not in kwargs:
        kwargs["datapath"] = os.path.dirname(__file__)

    file = os.path.join(kwargs["datapath"], filename)

    # download example weather data file in case it does not yet exist
    if not os.path.isfile(file):
        logging.debug("Download weather data for example.")
        req = requests.get("https://osf.io/59bqn/download")
        with open(file, "wb") as fout:
            fout.write(req.content)

    # read csv file
    weather_df = pd.read_csv(
        file,
        index_col=0,
        header=[0, 1],
        date_parser=lambda idx: pd.to_datetime(idx, utc=True),
    )

    # change time zone
    weather_df.index = weather_df.index.tz_convert("Europe/Berlin")

    return weather_df


def run_example():
    r"""
    Runs the example.

    """
    weather = get_weather_data("weather.csv")
    e126 = WindTurbine(
        **{
            "turbine_type": "E-126/4200",  # turbine type as in register
            "hub_height": 135,  # in m
        }
    )
    v90 = WindTurbine(
        **{
            "turbine_type": "V90/2000",  # turbine name as in register
            "hub_height": 120,  # in m
        }
    )

    # specification of wind farm data (2) containing a wind farm efficiency
    # wind turbine fleet is provided using the to_group function
    example_farm = WindFarm(
        **{
            "name": "example_farm_2",
            "wind_turbine_fleet": [
                v90.to_group(number_turbines=6),
                e126.to_group(total_capacity=12.6e6),
            ],
            "efficiency": 0.5
        }
    )

    example_cluster = WindTurbineCluster(**{
        "name": "Offshore_cluster",
        "wind_farms": [example_farm, example_farm],
    })

    # ModelChain with wind farm
    mc_farm = TurbineClusterModelChain(
        example_farm, wake_losses_model=None,
    ).run_model(weather)
    flh_farm = mc_farm.power_output.sum() / example_farm.nominal_power

    # ModelChain with wind cluster
    mc_cluster = TurbineClusterModelChain(
        example_cluster, wake_losses_model=None,
    ).run_model(weather)
    flh_cluster = mc_cluster.power_output.sum() / example_cluster.nominal_power

    print("Full Load Hours of cluster:", flh_cluster)
    print("Full Load Hours of farm:", flh_farm)


if __name__ == "__main__":
    run_example()
