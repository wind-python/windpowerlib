# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 10:30:27 2017

@author: RL-INSTITUT\sabine.haas
"""

"""
The ``modelchain`` module contains functions and classes of the windpowerlib.
This module makes it easy to get started with windpowerlib and demonstrates
standard ways to use the library.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from windpowerlib import (wind_speed, density, power_output)


class SimpleWindTurbine(object):
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    h_hub : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        The index should be the wind speed and a column should be named 'cp'.
    nominal_power : float
        The nominal output of the wind power plant.
    obstacle_height : float
            height of obstacles in m in the surroundings of the wind turbine,
            put obstacle_height to zero for wide spread obstacles
    wind_model : string
        Chooses the model for calculating the wind speed at hub height,
        Used in v_wind_hub;
        Possibilities: 'logarithmic', 'logarithmic_closest' (the weather data
            set messured closest to hub height is used.)
    rho_model : string
        Chooses the model for calculating the density of air at hub height,
        Used in rho_hub
        Possibilities:'barometric', 'ideal_gas'
    temperature_model : string
        Chooses the model for calculating the temperature at hub height,
        Used in rho_hub
        Possibilities: 'gradient', 'interpolation'
    tp_output_model : string
        Chooses the model for calculating the turbine power output,
        Used in turbine_power_output
        Possibilities: 'cp_values', 'p_values'

    Attributes
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    h_hub : float
        Height of the hub of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        The index should be the wind speed and a column should be named 'cp'.
    p_values : pandas.DataFrame
        The index should be the wind speed and a column should be named 'P'.
    nominal_power : float
        The nominal output of the wind power plant.
    obstacle_height : float
            height of obstacles in m in the surroundings of the wind turbine,
            put obstacle_height to zero for wide spread obstacles
    wind_model : string
        Chooses the model for calculating the wind speed at hub height,
        Used in v_wind_hub;
        Possibilities: 'logarithmic', 'logarithmic_closest' (the weather data
            set messured closest to hub height is used.)
    rho_model : string
        Chooses the model for calculating the density of air at hub height,
        Used in rho_hub
        Possibilities:'barometric', 'ideal_gas'
    temperature_model : string
        Chooses the model for calculating the temperature at hub height,
        Used in rho_hub
        Possibilities: 'gradient', 'interpolation'
    tp_output_model : string
        Chooses the model for calculating the turbine power output,
        Used in turbine_power_output
        Possibilities: 'cp_values', 'p_values'

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> enerconE126 = {
    ...    'h_hub': 135,
    ...    'd_rotor': 127,
    ...    'wind_conv_type': 'ENERCON E 126 7500'}
    >>> e126 = modelchain.SimpleWindTurbine(**enerconE126)
    >>> print(e126.d_rotor)
    127
    """

    def __init__(self, wind_conv_type=None, h_hub=None, d_rotor=None,
                 cp_values=None, p_values=None, nominal_power=None,
                 obstacle_height=0,
                 wind_model='logarithmic',
                 rho_model='barometric',
                 temperature_model='gradient',
                 tp_output_model='cp_values'):

        self.h_hub = h_hub
        self.d_rotor = d_rotor
        self.wind_conv_type = wind_conv_type
        self.cp_values = cp_values
        self.nominal_power = nominal_power
        self.p_values = p_values
        self.obstacle_height = obstacle_height

        # call models
        self.wind_model = wind_model
        self.rho_model = rho_model
        self.temperature_model = temperature_model
        self.tp_output_model = tp_output_model

    def rho_hub(self, weather, data_height, **kwargs):
        r"""
        Calculates the density of air in kg/m³ at hub height and the
        temperature T at hub height if their measurement or model height is not
        the same as hub height.
            (temperature in K, height in m, pressure in Pa)

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
        data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).

        Other parameters
        ----------------
        data_height_2 : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter for a second
            data height
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)

        Returns
        -------
        rho_hub : pandas.Series
            density of air in kg/m³ at hub height
        """
        # Check if temperature data is at hub height.
        if data_height['temp_air'] == self.h_hub:
            T_hub = weather.temp_air
            logging.info('The temperature was given at hub height of ' + str(
                         self.wind_conv_type) + '.')
        # Calculation of temperature in K at hub height according to the
        # chosen model.
        elif self.temperature_model == 'gradient':
            T_hub = density.temperature_gradient(weather, data_height,
                                                 self.h_hub)
            logging.info('The temperature at hub height of ' + str(
                         self.wind_conv_type) + ' was calculated with a ' +
                         'linear temperature gradient of -6.5 K/km.')
        elif self.temperature_model == 'interpolation':
            if kwargs.get('data_height_2') is None:
                sys.exit('There exists only one data height specification. ' +
                         'Add a second one or change temperature_model to ' +
                         'gradient.')
            elif kwargs.get('weather_2') is None:
                sys.exit('There exists only one weather data set. Add a ' +
                         'second one or change temperature_model to gradient.')
            else:
                T_hub = density.temperature_interpol(
                    weather, kwargs['weather_2'], data_height,
                    kwargs['data_height_2'], self.h_hub)
                # String for logging info
                if (self.h_hub > data_height['temp_air'] and
                        self.h_hub > kwargs['data_height_2']['temp_air']):
                    string = 'an extrapolation with'
                else:
                    string = 'an interpolation between'
                logging.info('The temperature at hub height of ' + str(
                             self.wind_conv_type) + ' was calculated with ' +
                             string + ' the temperatures measured at ' +
                             str(data_height['temp_air']) + ' m and ' +
                             str(kwargs['data_height_2']['temp_air']) + ' m.')
        else:
            sys.exit('invalid temperature_model in class SimpleWindTurbine; ' +
                     'model must be one of the following: gradient, interpol')

        # Calculation of density in kg/m³ at hub height according to the
        # chosen model.
        if self.rho_model == 'barometric':
            rho_hub = density.rho_barometric(weather, data_height,
                                             self.h_hub, T_hub)
            logging.info('The density at hub height of ' + str(
                         self.wind_conv_type) + ' was calculated with ' +
                         'the barometric height equation and a pressure ' +
                         'gradient of -1/8 hPa/m.')
        elif self.rho_model == 'ideal_gas':
            rho_hub = density.rho_ideal_gas(weather, data_height,
                                            self.h_hub, T_hub)
            logging.info('The density at hub height of ' + str(
                         self.wind_conv_type) + ' was calculated with ' +
                         'the ideal gas equation and a pressure ' +
                         'gradient of -1/8 hPa/m.')
        else:
            sys.exit('invalid rho_model in class SimpleWindTurbine; model ' +
                     'must be one of the following: barometric, ideal_gas')

        return rho_hub

    def v_wind_hub(self, weather, data_height, **kwargs):
        r"""
        Calculates the wind speed in m/s at hub height.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
        data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).

        Other parameters
        ----------------
        data_height_2 : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter for a second
            data height
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)

        Returns
        -------
        v_wind : pandas.Series
            wind speed [m/s] at hub height as time series
        """
        # Function for string for logging info
        def v_logging(wind_conv_type, data_height, obstacle_height):
            r"""
            Produces a string for the logging info.
            Parameters
            ----------
            wind_conv_type : string
                name of wind converter type
            data_height : float
                height of the wind speed data in m
            obstacle_height : float
                height of the surrounding obstacles in m

            Returns
            -------
            string
                string for logging info
            """
            return ('The wind speed at hub height of ' + str(
                    wind_conv_type) + ' was calculated with ' +
                    'the logarithmic height equation using wind speed ' +
                    'data of a height of ' + str(data_height) + ' m and an ' +
                    'obstacle height of ' + str(obstacle_height) + ' m.')

        # Check if wind speed data is at hub height.
        if data_height['v_wind'] == self.h_hub:
            v_wind = weather.v_wind
            logging.info('The wind speed was given at hub height of ' + str(
                         self.wind_conv_type) + '.')
        # Calculation of wind speed in m/s at hub height according to the
        # chosen model.
        elif self.wind_model == 'logarithmic':
            v_wind = wind_speed.logarithmic_wind_profile(self.h_hub,
                                                         weather, data_height,
                                                         self.obstacle_height)
            logging.info(v_logging(self.wind_conv_type, data_height['v_wind'],
                                   self.obstacle_height))
        elif self.wind_model == 'logarithmic_closest':
            if kwargs.get('data_height_2') is None:
                sys.exit('There exists only one data height specification. ' +
                         'Add a second one or change wind_model to ' +
                         'logarithmic.')
            elif kwargs.get('weather_2') is None:
                sys.exit('There exists only one weather data set. Add a ' +
                         'second one or change wind_model to logarithmic.')
            else:
                h_v_2 = kwargs['data_height_2']['v_wind']
                h_v_1 = data_height['v_wind']
                if abs(h_v_1 - self.h_hub) <= abs(h_v_2 - self.h_hub):
                    v_wind = wind_speed.logarithmic_wind_profile(
                        self.h_hub, weather, data_height, self.obstacle_height)
                    logging.info(v_logging(self.wind_conv_type,
                                           data_height['v_wind'],
                                           self.obstacle_height))
                else:
                    v_wind = wind_speed.logarithmic_wind_profile(
                        self.h_hub, kwargs['weather_2'],
                        kwargs['data_height_2'],
                        self.obstacle_height)
                    logging.info(v_logging(self.wind_conv_type,
                                 kwargs['data_height_2']['v_wind'],
                                 self.obstacle_height))
        else:
            sys.exit('invalid wind_model in class SimpleWindTurbine; model ' +
                     ' must be one of the following: logarithmic, ' +
                     'logarithmic_closest')
        return v_wind

    def fetch_wpp_data(self, **kwargs):
        r"""
        Fetch data of the requested wind converter.

        Returns
        -------
        tuple with pandas.DataFrame and float
            cp or P values and the nominal power
            of the requested wind converter

        Other parameters
        ----------------
        data_name : string
            name of the data for display in data frame (e.g. 'cp' or 'P')

        Examples
        --------
        >>> from windpowerlib import modelchain
        >>> e126 = modelchain.SimpleWindTurbine('ENERCON E 126 7500')
        >>> print(e126.cp_values.cp[5.0])
        0.423
        >>> print(e126.nominal_power)
        7500000.0
        """
        if 'data_name' not in kwargs:
            kwargs['data_name'] = 'cp'

        df = read_wpp_data(**kwargs)
        wpp_df = df[df.rli_anlagen_id == self.wind_conv_type]
        if wpp_df.shape[0] == 0:
            pd.set_option('display.max_rows', len(df))
            logging.info('Possible types: \n{0}'.format(df.rli_anlagen_id))
            pd.reset_option('display.max_rows')
            sys.exit('Cannot find the wind converter typ: {0}'.format(
                self.wind_conv_type))
        ncols = ['rli_anlagen_id', 'p_nenn', 'source', 'modificationtimestamp']
        data = np.array([0, 0])
        for col in wpp_df.keys():
            if col not in ncols:
                if wpp_df[col].iloc[0] is not None and not np.isnan(
                        float(wpp_df[col].iloc[0])):
                    data = np.vstack((data, np.array(
                        [float(col), float(wpp_df[col])])))
        data = np.delete(data, 0, 0)
        df = pd.DataFrame(data, columns=['v_wind', kwargs['data_name']])
        df.set_index('v_wind', drop=True, inplace=True)
        nominal_power = wpp_df['p_nenn'].iloc[0] * 1000
        return df, nominal_power

    def cp_series(self, v_wind):
        r"""
        Interpolates the cp value as a function of the wind velocity between
        data obtained from the power curve of the specified wind turbine type.

        Parameters
        ----------
        v_wind : pandas.Series or numpy.array
            Wind speed at hub height [m/s]

        Returns
        -------
        numpy.array
            cp values

        >>> import numpy
        >>> from windpowerlib import modelchain
        >>> e126 = modelchain.SimpleWindTurbine('ENERCON E 126 7500')
        >>> v_wind = numpy.array([1,2,3,4,5,6,7,8])
        >>> print(e126.cp_series(v_wind))
        [ 0.     0.     0.191  0.352  0.423  0.453  0.47   0.478]
        """
        v_max = self.cp_values.index.max()
        v_wind[v_wind > v_max] = v_max
        return np.interp(v_wind, self.cp_values.index, self.cp_values.cp)

    def turbine_power_output(self, weather, data_height, **kwargs):
        r"""
        Calculates the power output in W of one wind turbine.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
        data_height : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter

        Other parameters
        ----------------
        data_height_2 : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter for a second
            data height
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)

        Returns
        -------
        pandas.Series
            Electrical power of the wind turbine
        """
        if self.h_hub is None:
            sys.exit('Attribute h_hub (hub height) is missing.')
        if self.d_rotor is None:
            sys.exit('Attribute d_rotor (diameter of rotor) is missing.')

        # Calculation of parameters needed for power output
        v_wind = self.v_wind_hub(weather, data_height, **kwargs)
        rho_hub = self.rho_hub(weather, data_height, **kwargs)

        # Calculation of turbine power output according to the chosen model.
        if self.tp_output_model == 'cp_values':
            if self.cp_values is None or self.nominal_power is None:
                wpp_data = self.fetch_wpp_data()
            if self.cp_values is None:
                self.cp_values = wpp_data[0]
            if self.nominal_power is None:
                self.nominal_power = wpp_data[1]
            p_wpp = power_output.tpo_through_cp(
                weather, data_height, v_wind, rho_hub, self.d_rotor,
                self.cp_series(v_wind))
            logging.info('For the calculation of the power output of ' +
                         str(self.wind_conv_type) + ' a cp curve was used.')
        elif self.tp_output_model == 'p_values':
            if self.p_values is None or self.nominal_power is None:
                wpp_data = self.fetch_wpp_data(data_name='P',
                                               filename='P_values.csv')
            if self.p_values is None:
                self.p_values = wpp_data[0]
            if self.nominal_power is None:
                self.nominal_power = wpp_data[1]
            p_wpp = power_output.tpo_through_P(self.p_values, v_wind)
            logging.info('For the calculation of the power output of ' +
                         str(self.wind_conv_type) + ' a power curve was used.')
        else:
            sys.exit('invalid tp_output_model in class SimpleWindTurbine; ' +
                     'model must be one of the following: cp_values, ' +
                     'p_values')
        p_wpp_series = pd.Series(data=p_wpp,
                                 index=weather.index,
                                 name='feedin_wind_pp')
        p_wpp_series.index.names = ['']
        return p_wpp_series.clip(upper=(float(self.nominal_power)))


def read_wpp_data(**kwargs):
    r"""
    Fetch cp or P values from a file or download it from a server.

    The files are located in the data folder of the package root.

    Returns
    -------
    pandas.DataFrame
        cp or P values, wind converter type, installed capacity or the full
        table if the given wind converter cannot be found in the table.

    Other Parameters
    ----------------
    datapath : string, optional
        Path where the cp or P file is stored. Default: '$PACKAGE_ROOT/data'
    filename : string, optional
        Filename of the cp or P file.

    """
    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.join(os.path.dirname(__file__), 'data')

    if 'filename' not in kwargs:
        kwargs['filename'] = 'cp_values.csv'

    file = os.path.join(kwargs['datapath'], kwargs['filename'])

    df = pd.read_csv(file, index_col=0)
    return df


def get_wind_pp_types(print_out=True):
    r"""
    Get the names of all possible wind converter types.

    Parameters
    ----------
    print_out : boolean (default: True)
        Directly prints the list of types if set to True.

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> valid_types_df = modelchain.get_wind_pp_types(print_out=False)
    >>> valid_types_df.shape
    (91, 2)
    >>> print(valid_types_df.iloc[5])
    rli_anlagen_id    DEWIND D8 2000
    p_nenn                      2000
    Name: 5, dtype: object
    """
    df = read_wpp_data()

    if print_out:
        pd.set_option('display.max_rows', len(df))
        print(df[['rli_anlagen_id', 'p_nenn']])
        pd.reset_option('display.max_rows')
    return df[['rli_anlagen_id', 'p_nenn']]
