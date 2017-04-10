"""
The ``basic_example`` module shows a simple usage of the windpowerlib.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
import os
import pandas as pd

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from windpowerlib import modelchain
from windpowerlib import wind_turbine as wt

# Feel free to remove or change these lines
# import warnings
# warnings.simplefilter(action="ignore", category=RuntimeWarning)
logging.getLogger().setLevel(logging.INFO)


def read_weather_data(filename, datetime_column='Unnamed: 0',
                      **kwargs):
    r"""
    Fetches weather data from a file.

    The files are located in the example folder of the windpowerlib.

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

# Read weather data from csv
weather = read_weather_data('weather.csv')

# Specification of the weather data set CoastDat2 (example data)
coastDat2 = {
    'dhi': 0,
    'dirhi': 0,
    'pressure': 0,
    'temp_air': 2,
    'v_wind': 10,
    'Z0': 0,
    'temp_air_2': 10,
    'v_wind_2': 80}

# Specifications of the wind turbines
enerconE126 = {
    'hub_height': 135,
    'd_rotor': 127,
    'turbine_name': 'ENERCON E 126 7500'}

vestasV90 = {
    'hub_height': 105,
    'd_rotor': 90,
    'turbine_name': 'VESTAS V 90 3000'}

# Initialize WindTurbine objects
e126 = wt.WindTurbine(**enerconE126)
v90 = wt.WindTurbine(**vestasV90)

# Specifications of the modelchain data
modelchain_data = {
    'obstacle_height': 0,
    'wind_model': 'logarithmic',
    'rho_model': 'ideal_gas',
    'temperature_model': 'interpolation',
    'power_output_model': 'cp_values',
    'density_corr': False}

# Calculate turbine power output
mc_e126 = modelchain.Modelchain(e126, **modelchain_data).run_model(
    weather, coastDat2)
e126.power_output = mc_e126.power_output
mc_v90 = modelchain.Modelchain(v90, **modelchain_data).run_model(
    weather, coastDat2)
v90.power_output = mc_v90.power_output

# Plot turbine power output
if plt:
    e126.power_output.plot(legend=True, label='Enercon E126')
    v90.power_output.plot(legend=True, label='Vestas V90')
    plt.show()
else:
    print(e126.power_output)
    print(v90.power_output)

# Plot power (coefficient) curves
if plt:
    if e126.cp_values is not None:
        e126.cp_values.plot(style='*', title='Enercon E126')
        plt.show()
    if e126.p_values is not None:
        e126.p_values.plot(style='*', title='Enercon E126')
        plt.show()
    if v90.cp_values is not None:
        v90.cp_values.plot(style='*', title='Vestas V90')
        plt.show()
    if v90.p_values is not None:
        v90.p_values.plot(style='*', title='Vestas V90')
        plt.show()
else:
    if e126.cp_values is not None:
        print("The cp value at a wind speed of 5 m/s: {0}".format(
            e126.cp_values.cp[5.0]))
    if e126.p_values is not None:
        print("The P value at a wind speed of 5 m/s: {0}".format(
            e126.p_values.P[5.0]))
logging.info('Done!')
