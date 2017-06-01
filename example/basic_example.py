"""
The ``basic_example`` module shows a simple usage of the windpowerlib.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import os
import pandas as pd

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from windpowerlib import modelchain
from windpowerlib import wind_turbine as wt

# You can use the logging package to get logging messages from the windpowerlib
# Change the logging level if you want more or less messages
import logging
logging.getLogger().setLevel(logging.DEBUG)


def get_weather_data(filename, datetime_column='time_index', **kwargs):
    r"""
    Imports weather data from a file and specifies height of weather data.

    The data include wind speed at two different heights in m/s, air
    temperature in two different heights in K, surface roughness length in m
    and air pressure in Pa.

    Parameters
    ----------
    filename : string
        Filename of the weather data file.
    datetime_column : string
            Name of the datetime column of the weather DataFrame.
            Default: 'time_index'.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the weather data file is stored.
        Default: 'windpowerlib/example'.

    Returns
    -------
    Tuple (pd.DataFrame, dictionary)
        `weather` DataFrame contains weather data time series.
        `data_height` dictionary contains height for which corresponding
        weather data applies.

    """
    def read_weather_data(filename, datetime_column='time_index',
                          **kwargs):
        r"""
        Fetches weather data from a file.

        The file is located in the example folder of the windpowerlib.

        Parameters
        ----------
        filename : string
            Filename of the weather data file.
        datetime_column : string
            Name of the datetime column of the weather DataFrame.

        Other Parameters
        ----------------
        datapath : string, optional
            Path where the weather data file is stored.
            Default: 'windpowerlib/example'.

        Returns
        -------
        pandas.DataFrame
            Contains weather data time series.

        """
        if 'datapath' not in kwargs:
            kwargs['datapath'] = os.path.join(os.path.split(
                os.path.dirname(__file__))[0], 'example')

        file = os.path.join(kwargs['datapath'], filename)
        df = pd.read_csv(file)
        return df.set_index(pd.to_datetime(df[datetime_column])).tz_localize(
            'UTC').tz_convert('Europe/Berlin').drop(datetime_column, 1)

    # read weather data from csv
    weather = read_weather_data(filename=filename,
                                datetime_column=datetime_column, **kwargs)

    # dictionary specifying the height for which the weather data applies
    # data in m
    data_height = {
        'pressure': 0,
        'temp_air': 2,
        'v_wind': 10,
        'temp_air_2': 10,
        'v_wind_2': 80}

    return (weather, data_height)


def initialise_wind_turbines():
    r"""
    Initialises two :class:`~.wind_turbine.WindTurbine` objects.

    Function shows two ways to initialise a WindTurbine object. You can either
    specify your own turbine, as done below for 'myTurbine', or fetch power
    and/or power coefficient curve data from data files provided by the
    windpowerlib, as done for the 'enerconE126'.
    Execute ``windpowerlib.wind_turbine.get_turbine_types()`` or
    ``windpowerlib.wind_turbine.get_turbine_types(filename='cp_curves.csv')``
    to get a list of all wind turbines for which power and power coefficient
    curves respectively are provided.

    Returns
    -------
    Tuple (WindTurbine, WindTurbine)

    """

    # specification of own wind turbine (Note: power coefficient values and
    # nominal power have to be in Watt)
    myTurbine = {
        'turbine_name': 'myTurbine',
        'nominal_power': 3e6,  # in W
        'hub_height': 105,  # in m
        'd_rotor': 90,  # in m
        'p_values': pd.DataFrame(
            data={'p': [p * 1000 for p in
                        [0.0, 26.0, 180.0, 1500.0, 3000.0, 3000.0]]},  # in W
            index=[0.0, 3.0, 5.0, 10.0, 15.0, 25.0])  # in m/s
    }
    # initialise WindTurbine object
    my_turbine = wt.WindTurbine(**myTurbine)

    # specification of wind turbine where power curve is provided
    # if you want to use the power coefficient curve add {'fetch_curve': 'cp'}
    # to the dictionary
    enerconE126 = {
        'turbine_name': 'ENERCON E 126 7500',  # turbine name as in register
        'hub_height': 135,  # in m
        'd_rotor': 127  # in m
    }
    # initialise WindTurbine object
    e126 = wt.WindTurbine(**enerconE126)

    return (my_turbine, e126)


def calculate_power_output(weather, data_height, my_turbine, e126):
    r"""
    Calculates power output of wind turbines using the
    :class:`~.modelchain.ModelChain`.

    The :class:`~.modelchain.ModelChain` is a class that provides all necessary
    steps to calculate the power output of a wind turbine. You can either use
    the default methods for the calculation steps, as done for 'my_turbine',
    or choose different methods, as done for the 'e126'.

    Parameters
    ----------
    weather : pd.DataFrame
        Contains weather data time series.
    data_height : dictionary
        Contains height for which corresponding weather data applies.
    my_turbine : WindTurbine
        WindTurbine object with self provided power curve.
    e126 : WindTurbine
        WindTurbine object with power curve from data file provided by the
        windpowerlib.

    """

    # power output calculation for my_turbine
    # initialise ModelChain with default parameters and use run_model method
    # to calculate power output
    mc_my_turbine = modelchain.ModelChain(my_turbine).run_model(
        weather, data_height)
    # write power output timeseries to WindTurbine object
    my_turbine.power_output = mc_my_turbine.power_output

    # power output calculation for e126
    # own specifications for ModelChain setup
    modelchain_data = {
        'obstacle_height': 0,  # default: 0
        'wind_model': 'logarithmic',  # 'logarithmic' (default) or 'hellman'
        'rho_model': 'ideal_gas',  # 'barometric' (default) or 'ideal_gas'
        'power_output_model': 'p_values',  # 'p_values' (default) or
                                           # 'cp_values'
        'density_corr': True,  # False (default) or True
        'hellman_exp': None}  # None (default) or None
    # initialise ModelChain with own specifications and use run_model method
    # to calculate power output
    mc_e126 = modelchain.ModelChain(e126, **modelchain_data).run_model(
        weather, data_height)
    # write power output timeseries to WindTurbine object
    e126.power_output = mc_e126.power_output

    return


def plot_or_print(my_turbine, e126):
    r"""
    Plots or prints power output and power (coefficient) curves.

    Parameters
    ----------
    my_turbine : WindTurbine
        WindTurbine object with self provided power curve.
    e126 : WindTurbine
        WindTurbine object with power curve from data file provided by the
        windpowerlib.

    """

    # plot or print turbine power output
    if plt:
        e126.power_output.plot(legend=True, label='Enercon E126')
        my_turbine.power_output.plot(legend=True, label='myTurbine')
        plt.show()
    else:
        print(e126.power_output)
        print(my_turbine.power_output)

    # plot or print power (coefficient) curve
    if plt:
        if e126.cp_values is not None:
            e126.cp_values.plot(style='*', title='Enercon E126')
            plt.show()
        if e126.p_values is not None:
            e126.p_values.plot(style='*', title='Enercon E126')
            plt.show()
        if my_turbine.cp_values is not None:
            my_turbine.cp_values.plot(style='*', title='myTurbine')
            plt.show()
        if my_turbine.p_values is not None:
            my_turbine.p_values.plot(style='*', title='myTurbine')
            plt.show()
    else:
        if e126.cp_values is not None:
            print(e126.cp_values)
        if e126.p_values is not None:
            print("The P value at a wind speed of 5 m/s: {0}".format(
                e126.p_values.P[5.0]))


def run_basic_example():
    r"""
    Run the basic example.

    """
    weather, data_height = get_weather_data('weather.csv')
    my_turbine, e126 = initialise_wind_turbines()
    calculate_power_output(weather, data_height, my_turbine, e126)
    plot_or_print(my_turbine, e126)


if __name__ == "__main__":
    run_basic_example()