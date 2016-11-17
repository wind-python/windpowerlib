#!/usr/bin/python3
# -*- coding: utf-8

import pandas as pd
import logging
import os
import requests

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from windpowerlib import basicmodel

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
    'Z0': 0}

# Specifications of the wind turbines
enerconE126 = {
    'h_hub': 135,
    'd_rotor': 127,
    'wind_conv_type': 'ENERCON E 126 7500'}

vestasV90 = {
    'h_hub': 105,
    'd_rotor': 90,
    'wind_conv_type': 'VESTAS V 90 3000'}


def download_file(filename, url):
    if not os.path.isfile(filename):
        logging.info('Copying weather data from {0} to {1}'.format(
            url, filename))
        req = requests.get(url)
        with open(filename, 'wb') as fout:
            fout.write(req.content)

def fetch_example_files():
    basic_path = os.path.join(os.path.expanduser("~"), '.oemof')
    filename_1 = os.path.join(basic_path, 'weather.csv')
    url1 = 'http://vernetzen.uni-flensburg.de/~git/weather.csv'
    filename_2 = os.path.join(basic_path, 'weather_wittenberg.csv')
    url2 = 'http://vernetzen.uni-flensburg.de/~git/weather_wittenberg.csv'
    if not os.path.exists(basic_path):
        os.makedirs(basic_path)
    download_file(filename_1, url1)
    download_file(filename_2, url2)
    return filename_1, filename_2


def ready_example_data(filename, datetime_column='Unnamed: 0'):
    df = pd.read_csv(filename)
    return df.set_index(pd.to_datetime(df[datetime_column])).tz_localize(
        'UTC').tz_convert('Europe/Berlin').drop(datetime_column, 1)


filename1, filename2 = fetch_example_files()

# Loading weather data
weather_df = ready_example_data(filename1)

e126 = basicmodel.SimpleWindTurbine(**enerconE126)
v90 = basicmodel.SimpleWindTurbine(**vestasV90)

if plt:
    e126.cp_values.plot(style='*')
    plt.show()
else:
    print("The cp value at a wind speed of 5 m/s: {0}".format(
        e126.cp_values.cp[5.0]))

if plt:
    e126.turbine_power_output(weather=weather_df, data_height=coastDat2).plot(
        legend=True, label='Enercon E126')
    v90.turbine_power_output(weather=weather_df, data_height=coastDat2).plot(
        legend=True, label='Vestas V90')
    plt.show()
else:
    print(v90.turbine_power_output(weather=weather_df, data_height=coastDat2))

logging.info('Done!')
