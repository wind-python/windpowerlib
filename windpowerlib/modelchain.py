"""The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"

import os
import sys
import logging
import numpy as np
import pandas as pd
from windpowerlib import wind_speed, density, power_output


class Modelchain(object):
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    hub_height : float
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
            set measured closest to hub height is used.)
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
        Possibilities: 'cp_values', 'p_values', 'P_curve_correction'
    density_corr : boolean
        if True -> density corrected power curve

    Attributes
    ----------
    wind_conv_type : string
        Name of the wind converter type. Use get_wind_pp_types() to see a list
        of all possible wind converters.
    hub_height : float
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
            set measured closest to hub height is used.)
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
    density_corr : boolean
        if True -> density corrected power curve

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'd_rotor': 127,
    ...    'wind_conv_type': 'ENERCON E 126 7500'}
    >>> e126 = modelchain.SimpleWindTurbine(**enerconE126)
    >>> print(e126.d_rotor)
    127
    """

    def __init__(self, wind_conv_type=None, hub_height=None, d_rotor=None,
                 cp_values=None, p_values=None, nominal_power=None,
                 obstacle_height=0,
                 wind_model='logarithmic',
                 rho_model='barometric',
                 temperature_model='gradient',
                 tp_output_model='cp_values',
                 density_corr=False):

        self.hub_height = hub_height
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
        self.density_corr = density_corr

    def rho_hub(self, weather, data_height, **kwargs):
        r"""
        Calculates the density of air at hub height.

        Within the function the temperature at hub height is calculated as
        well if it is not given at hub height.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for temperature
            (temp_air) and pressure (pressure)
                data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply

        Other parameters
        ----------------
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for temperature
            (temp_air) and pressure (pressure)
        data_height_2 : dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air) and pressure (pressure)

        Returns
        -------
        rho_hub : pandas.Series or array
            density of air in kg/m³ at hub height
        """
        # Check if temperature data is at hub height.
        if data_height['temp_air'] == self.hub_height:
            logging.debug('Using given temperature (at hub height).')
            T_hub = weather['temp_air']
        # Calculation of temperature in K at hub height according to the
        # chosen model.
        elif self.temperature_model == 'gradient':
            logging.debug('Calculating temperature with gradient.')
            T_hub = density.temperature_gradient(
                weather['temp_air'], data_height['temp_air'], self.hub_height)
        elif self.temperature_model == 'interpolation':
            if 'data_height_2' not in kwargs or 'weather_2' not in kwargs:
                logging.info('One weather data set or data height set is ' +
                             'missing. It was calculated with a temperature ' +
                             'gradient.')
                T_hub = density.temperature_gradient(
                    weather['temp_air'], data_height['temp_air'],
                    self.hub_height)
            # Check if temperature data of second data set is at hub height.
            elif kwargs['data_height_2']['temp_air'] == self.hub_height:
                logging.debug('Using given temperature (at hub height).')
                T_hub = kwargs['weather_2']['temp_air']
            else:
                logging.debug('Calculating temperature with interpolation.')
                T_hub = density.temperature_interpol(
                    weather['temp_air'], kwargs['weather_2']['temp_air'],
                    data_height['temp_air'],
                    kwargs['data_height_2']['temp_air'], self.hub_height)
        else:
            logging.info('wrong value: `temperature_model` must be gradient ' +
                         'or interpolation. It was calculated with gradient.')
            T_hub = density.temperature_gradient(
                weather['temp_air'], data_height['temp_air'], self.hub_height)

        # Calculation of density in kg/m³ at hub height according to the
        # chosen model.
        if self.rho_model == 'barometric':
            logging.debug('Calculating density with barometric height eq.')
            rho_hub = density.rho_barometric(weather['pressure'],
                                             data_height['pressure'],
                                             self.hub_height, T_hub)
        elif self.rho_model == 'ideal_gas':
            logging.debug('Calculating density with ideal gas equation.')
            rho_hub = density.rho_ideal_gas(weather['pressure'],
                                            data_height['pressure'],
                                            self.hub_height, T_hub)
        else:
            logging.info('wrong value: `rho_model` must be barometric ' +
                         'or ideal_gas. It was calculated with barometric.')
            rho_hub = density.rho_barometric(weather['pressure'],
                                             data_height['pressure'],
                                             self.hub_height, T_hub)
        return rho_hub

    def v_wind_hub(self, weather, data_height, **kwargs):
        r"""
        Calculates the wind speed at hub height.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            (v_wind) and roughness length (z0)
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply

        Other parameters
        ----------------
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
        data_height_2 : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter for a second
            data height

        Returns
        -------
        v_wind : pandas.Series or array
            wind speed [m/s] at hub height as time series
        """
        # Check if wind speed data is at hub height.
        if data_height['v_wind'] == self.hub_height:
            logging.debug('Using given wind speed (at hub height).')
            v_wind = weather['v_wind']
        # Calculation of wind speed in m/s at hub height according to the
        # chosen model.
        elif self.wind_model == 'logarithmic':
            logging.debug('Calculating v_wind with logarithmic wind profile.')
            v_wind = wind_speed.logarithmic_wind_profile(
                weather['v_wind'], data_height['v_wind'], self.hub_height,
                weather['z0'], self.obstacle_height)
        elif self.wind_model == 'logarithmic_closest':
            if 'data_height_2' not in kwargs or 'weather_2' not in kwargs:
                logging.info('One weather data set or data height set is ' +
                             'missing. It was calculated with one data set.')
                v_wind = wind_speed.logarithmic_wind_profile(
                    weather['v_wind'], data_height['v_wind'], self.hub_height,
                    weather['z0'], self.obstacle_height)
            # Check if wind speed of second data set is at hub height.
            elif kwargs['data_height_2']['v_wind'] == self.hub_height:
                logging.debug('Using given wind speed (at hub height).')
                v_wind = kwargs['weather_2']['v_wind']
            else:
                logging.debug('Calculating v_wind with logarithmic wind ' +
                              'profile.')
                h_v_2 = kwargs['data_height_2']['v_wind']
                h_v_1 = data_height['v_wind']
                if (abs(h_v_1 - self.hub_height) <=
                        abs(h_v_2 - self.hub_height)):
                    v_wind = wind_speed.logarithmic_wind_profile(
                        weather['v_wind'], data_height['v_wind'],
                        self.hub_height, weather['z0'], self.obstacle_height)
                else:
                    v_wind = wind_speed.logarithmic_wind_profile(
                        kwargs['weather_2']['v_wind'],
                        kwargs['data_height_2']['v_wind'], self.hub_height,
                        kwargs['weather_2']['z0'], self.obstacle_height)
        else:
            logging.info('wrong value: `wind_model` must be logarithmic or' +
                         'logarithmic_closest. It was calculated with ' +
                         'logarithmic.')
            v_wind = wind_speed.logarithmic_wind_profile(
                weather['v_wind'], data_height['v_wind'], self.hub_height,
                weather['z0'], self.obstacle_height)
        return v_wind

    def fetch_wpp_data(self, **kwargs):
        r"""
        Fetches data of the requested wind converter.

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
        Converts the curve of the power coefficient to a time series.

        Interpolates the power coefficient as a function of the wind speed
        between data obtained from the cp curve of the specified wind turbine
        type.

        Parameters
        ----------
        v_wind : pandas.Series or array
            wind speed at hub height in m/s

        Returns
        -------
        numpy.array
            cp values for the wind speed time series

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
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply

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
        if self.hub_height is None:
            sys.exit('Attribute hub_height (hub height) is missing.')
        if self.d_rotor is None:
            sys.exit('Attribute d_rotor (diameter of rotor) is missing.')

        # Calculation of parameters needed for power output
        v_wind = self.v_wind_hub(weather, data_height, **kwargs)
        rho_hub = self.rho_hub(weather, data_height, **kwargs)

        # Calculation of turbine power output according to the chosen model.
        if self.tp_output_model == 'cp_values':
            # get cp values and/or nominal power
            if self.cp_values is None or self.nominal_power is None:
                wpp_data = self.fetch_wpp_data()
                if self.cp_values is None:
                    self.cp_values = wpp_data[0]
                if self.nominal_power is None:
                    self.nominal_power = wpp_data[1]
            if self.density_corr is False:
                logging.debug('Calculating power output with cp curve.')
                p_wpp = power_output.tpo_through_cp(
                    v_wind, rho_hub, self.d_rotor, self.cp_series(v_wind))
            elif self.density_corr is True:
                logging.debug('Calculating power output with density ' +
                              'corrected cp curve.')
                # get P curve from cp values with ambient density = 1.225 kg/m³
                p_curve = power_output.tpo_through_cp(
                    self.cp_values.index, 1.225, self.d_rotor,
                    self.cp_values.cp)
                p_df = pd.DataFrame(data=p_curve, index=self.cp_values.index)
                p_df.columns = ['P']
                # density correction of P and electrical time series
                p_wpp = power_output.interpolate_P_curve(v_wind, rho_hub,
                                                         p_df)
            else:
                logging.info('wrong value: `density_corr` must be True or ' +
                             'False. It was calculated with the value False.')
                p_wpp = power_output.tpo_through_cp(
                    v_wind, rho_hub, self.d_rotor, self.cp_series(v_wind))

        elif self.tp_output_model == 'p_values':
            # get P values and/or nominal power
            if self.p_values is None or self.nominal_power is None:
                wpp_data = self.fetch_wpp_data(data_name='P',
                                               filename='P_values.csv')
                if self.p_values is None:
                    self.p_values = wpp_data[0]*1000
                if self.nominal_power is None:
                    self.nominal_power = wpp_data[1]
            if self.density_corr is False:
                logging.debug('Calculating power output with power curve.')
                p_wpp = power_output.tpo_through_P(self.p_values, v_wind)
            if self.density_corr is True:
                logging.debug('Calculating power output with density ' +
                              'corrected power curve.')
                p_wpp = power_output.interpolate_P_curve(v_wind, rho_hub,
                                                         self.p_values)
        else:
            logging.info('wrong value: `tp_output_model` must be cp_values ' +
                         'or p_values. It was calculated with cp_values and ' +
                         'without density correction.')
            if self.cp_values is None or self.nominal_power is None:
                wpp_data = self.fetch_wpp_data()
                if self.cp_values is None:
                    self.cp_values = wpp_data[0]
                if self.nominal_power is None:
                    self.nominal_power = wpp_data[1]
            p_wpp = power_output.tpo_through_cp(v_wind, rho_hub, self.d_rotor,
                                                self.cp_series(v_wind))
        p_wpp_series = pd.Series(data=p_wpp,
                                 index=weather.index,
                                 name='feedin_wind_pp')
        p_wpp_series.index.names = ['']
        return p_wpp_series.clip(upper=(float(self.nominal_power)))


def read_wpp_data(**kwargs):
    r"""
    Fetches cp or P values from a file or downloads it from a server.

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
