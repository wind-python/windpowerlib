"""
The ``modelchain_example`` module shows a simple usage of the windpowerlib by
using the :class:`~.modelchain.ModelChain` class. The modelchains are
implemented to ensure an easy start into the Windpowerlib. They work like
models that combine all functions provided in the library. Via parameters
desired functions of the windpowerlib can be selected. For parameters not being
specified default parameters are used.

There are mainly three steps. First you have to import your weather data, then
you need to specify your wind turbine, and in the last step call the
windpowerlib functions to calculate the feed-in time series.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import os
import pandas as pd

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from windpowerlib import ModelChain
from windpowerlib import WindTurbine

# You can use the logging package to get logging messages from the windpowerlib
# Change the logging level if you want more or less messages
import logging
logging.getLogger().setLevel(logging.DEBUG)


def get_weather_data(filename='weather.csv', **kwargs):
    r"""
    Imports weather data from a file.

    The data include wind speed at two different heights in m/s, air
    temperature in two different heights in K, surface roughness length in m
    and air pressure in Pa. The file is located in the example folder of the
    windpowerlib. The height in m for which the data applies is specified in
    the second row.

    Parameters
    ----------
    filename : str
        Filename of the weather data file. Default: 'weather.csv'.

    Other Parameters
    ----------------
    datapath : str, optional
        Path where the weather data file is stored.
        Default: 'windpowerlib/example'.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for wind speed `wind_speed` in m/s,
            temperature `temperature` in K, roughness length `roughness_length`
            in m, and pressure `pressure` in Pa.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name as string (e.g. 'wind_speed') and the
            second level contains the height as integer at which it applies
            (e.g. 10, if it was measured at a height of 10 m).

    """

    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.split(
            os.path.dirname(__file__))[0], 'example')
    file = os.path.join(kwargs['datapath'], filename)

    # read csv file
    weather_df = pd.read_csv(
        file, index_col=0, header=[0, 1],
        date_parser=lambda idx: pd.to_datetime(idx, utc=True))

    # change type of index to datetime and set time zone
    weather_df.index = pd.to_datetime(weather_df.index).tz_convert(
        'Europe/Berlin')

    # change type of height from str to int by resetting columns
    l0 = [_[0] for _ in weather_df.columns]
    l1 = [int(_[1]) for _ in weather_df.columns]
    weather_df.columns = [l0, l1]

    return weather_df


def initialize_wind_turbines():
    r"""
    Initializes three :class:`~.wind_turbine.WindTurbine` objects.

    This function shows three ways to initialize a WindTurbine object. You can
    either use turbine data from the OpenEnergy Database (oedb) turbine library
    that is provided along with the windpowerlib, as done for the
    'enercon_e126', or specify your own turbine by directly providing a power
    (coefficient) curve, as done below for 'my_turbine', or provide your own
    turbine data in csv files, as done for 'dummy_turbine'.

    To get a list of all wind turbines for which power and/or power coefficient
    curves are provided execute `
    `windpowerlib.wind_turbine.get_turbine_types()``.

    Returns
    -------
    Tuple (:class:`~.wind_turbine.WindTurbine`,
           :class:`~.wind_turbine.WindTurbine`,
           :class:`~.wind_turbine.WindTurbine`)

    """

    # specification of wind turbine where data is provided in the oedb
    # turbine library
    enercon_e126 = {
        'turbine_type': 'E-126/4200',  # turbine type as in register
        'hub_height': 135  # in m
    }
    # initialize WindTurbine object
    e126 = WindTurbine(**enercon_e126)

    # specification of own wind turbine (Note: power values and nominal power
    # have to be in Watt)
    my_turbine = {
        'nominal_power': 3e6,  # in W
        'hub_height': 105,  # in m
        'power_curve': pd.DataFrame(
            data={'value': [p * 1000 for p in [
                      0.0, 26.0, 180.0, 1500.0, 3000.0, 3000.0]],  # in W
                  'wind_speed': [0.0, 3.0, 5.0, 10.0, 15.0, 25.0]})  # in m/s
    }
    # initialize WindTurbine object
    my_turbine = WindTurbine(**my_turbine)

    # specification of wind turbine where power coefficient curve and nominal
    # power is provided in an own csv file
    csv_path = os.path.join(os.path.dirname(__file__), 'data')
    dummy_turbine = {
        'turbine_type': "DUMMY 1",
        'hub_height': 100,  # in m
        'rotor_diameter': 70,  # in m
        'path': csv_path
    }
    # initialize WindTurbine object
    dummy_turbine = WindTurbine(**dummy_turbine)

    return my_turbine, e126, dummy_turbine


def calculate_power_output(weather, my_turbine, e126, dummy_turbine):
    r"""
    Calculates power output of wind turbines using the
    :class:`~.modelchain.ModelChain`.

    The :class:`~.modelchain.ModelChain` is a class that provides all necessary
    steps to calculate the power output of a wind turbine. You can either use
    the default methods for the calculation steps, as done for 'my_turbine',
    or choose different methods, as done for the 'e126'. Of course, you can
    also use the default methods while only changing one or two of them, as
    done for 'dummy_turbine'.

    Parameters
    ----------
    weather : :pandas:`pandas.DataFrame<frame>`
        Contains weather data time series.
    my_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with self provided power curve.
    e126 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power curve from the OpenEnergy Database
        turbine library.
    dummy_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power coefficient curve from example file.

    """

    # power output calculation for my_turbine
    # initialize ModelChain with default parameters and use run_model method
    # to calculate power output
    mc_my_turbine = ModelChain(my_turbine).run_model(weather)
    # write power output time series to WindTurbine object
    my_turbine.power_output = mc_my_turbine.power_output

    # power output calculation for e126
    # own specifications for ModelChain setup
    modelchain_data = {
        'wind_speed_model': 'logarithmic',  # 'logarithmic' (default),
                                            # 'hellman' or
                                            # 'interpolation_extrapolation'
        'density_model': 'ideal_gas',  # 'barometric' (default), 'ideal_gas' or
                                       # 'interpolation_extrapolation'
        'temperature_model': 'linear_gradient',  # 'linear_gradient' (def.) or
                                                 # 'interpolation_extrapolation'
        'power_output_model': 'power_curve',  # 'power_curve' (default) or
                                              # 'power_coefficient_curve'
        'density_correction': True,  # False (default) or True
        'obstacle_height': 0,  # default: 0
        'hellman_exp': None}  # None (default) or None
    # initialize ModelChain with own specifications and use run_model method
    # to calculate power output
    mc_e126 = ModelChain(e126, **modelchain_data).run_model(weather)
    # write power output time series to WindTurbine object
    e126.power_output = mc_e126.power_output

    # power output calculation for example_turbine
    # own specification for 'power_output_model'
    mc_example_turbine = ModelChain(
        dummy_turbine,
        power_output_model='power_coefficient_curve').run_model(weather)
    dummy_turbine.power_output = mc_example_turbine.power_output

    return


def plot_or_print(my_turbine, e126, dummy_turbine):
    r"""
    Plots or prints power output and power (coefficient) curves.

    Parameters
    ----------
    my_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with self provided power curve.
    e126 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power curve from the OpenEnergy Database
        turbine library.
    dummy_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power coefficient curve from example file.

    """

    # plot or print turbine power output
    if plt:
        e126.power_output.plot(legend=True, label='Enercon E126')
        my_turbine.power_output.plot(legend=True, label='myTurbine')
        dummy_turbine.power_output.plot(legend=True, label='dummyTurbine')
        plt.xlabel('Time')
        plt.ylabel('Power in W')
        plt.show()
    else:
        print(e126.power_output)
        print(my_turbine.power_output)
        print(dummy_turbine.power_output)

    # plot or print power curve
    if plt:
        if e126.power_curve is not False:
            e126.power_curve.plot(x='wind_speed', y='value', style='*',
                                  title='Enercon E126 power curve')
            plt.xlabel('Wind speed in m/s')
            plt.ylabel('Power in W')
            plt.show()
        if my_turbine.power_curve is not False:
            my_turbine.power_curve.plot(x='wind_speed', y='value', style='*',
                                        title='myTurbine power curve')
            plt.xlabel('Wind speed in m/s')
            plt.ylabel('Power in W')
            plt.show()
        if dummy_turbine.power_coefficient_curve is not False:
            dummy_turbine.power_coefficient_curve.plot(
                x='wind_speed', y='value', style='*',
                title='dummyTurbine power coefficient curve')
            plt.xlabel('Wind speed in m/s')
            plt.ylabel('Power coefficient')
            plt.show()
    else:
        if e126.power_coefficient_curve is not False:
            print(e126.power_coefficient_curve)
        if e126.power_curve is not False:
            print(e126.power_curve)


def run_example():
    r"""
    Runs the basic example.

    """
    weather = get_weather_data('weather.csv')
    my_turbine, e126, dummy_turbine = initialize_wind_turbines()
    calculate_power_output(weather, my_turbine, e126, dummy_turbine)
    plot_or_print(my_turbine, e126, dummy_turbine)


if __name__ == "__main__":
    run_example()
