"""The ``basic_example`` module shows a simple usage of the windpowerlib.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"

import logging

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

# Specifications of the modelchain data
modelchain_data = {
    'obstacle_height': 0,
    'wind_model': 'logarithmic_closest',
    'rho_model': 'ideal_gas',
    'temperature_model': 'interpolation',
    'power_output_model': 'cp_values',
    'density_corr': False}


e126 = wt.WindTurbine(**enerconE126)
v90 = wt.WindTurbine(**vestasV90)

modelchain.Modelchain(e126, **modelchain_data).run_model(coastDat2)
modelchain.Modelchain(v90, **modelchain_data).run_model(coastDat2)

if plt:
    e126.power_output.plot(legend=True, label='Enercon E126')
    v90.power_output.plot(legend=True, label='Vestas V90')
    plt.show()
else:
    print(e126.power_output)
    print(v90.power_output)

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
