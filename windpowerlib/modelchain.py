"""The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"

import os
import logging
import numpy as np
import pandas as pd
from windpowerlib import wind_speed, density, power_output


class Modelchain(object):
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    wind_turbine : list or tuple of objects of the class WindTurbine
        Objects contain attributes `turbine_name`, `hub_height`, `d_rotor`,
        `cp_values` or/and `p_values` and `nominal_power`.
        If only one object exists it is an item of a list.
    obstacle_height : float, optional
        Height of obstacles in the surroundings of the wind turbine. Put
        obstacle_height to zero for wide spread obstacles. Default: 0
    wind_model : string, optional
        Chooses the model for calculating the wind speed at hub height.
        Used in v_wind_hub.
        Possibilities: 'logarithmic', 'logarithmic_closest' (The weather data
            set measured closest to hub height is used.).
    rho_model : string, optional
        Chooses the model for calculating the density of air at hub height.
        Used in rho_hub. Possibilities:'barometric', 'ideal_gas'.
    temperature_model : string, optional
        Chooses the model for calculating the temperature at hub height.
        Used in rho_hub. Possibilities: 'gradient', 'interpolation'.
    tp_output_model : string, optional
        Chooses the model for calculating the turbine power output.
        Used in turbine_power_output.
        Possibilities: 'cp_values', 'p_values', 'P_curve_correction'.
    density_corr : boolean, optional
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False

    Attributes
    ----------
    wind_turbine : list or tuple of objects of the class WindTurbine
        Objects contain attributes `turbine_name`, `hub_height`, `d_rotor`,
        `cp_values` or/and `p_values` and `nominal_power`.
        If only one object exists it is an item of a list.
    obstacle_height : float, optional
        Height of obstacles in the surroundings of the wind turbine. Put
        obstacle_height to zero for wide spread obstacles. Default: 0
    hub_height : float
        Hub height of the wind turbine.
    d_rotor : float
        Diameter of the rotor.
    cp_values : pandas.DataFrame
        Curve of the power coefficient of the wind turbine.
        The indices are the corresponding wind speeds of the power coefficient
        curve, the power coefficient values containing column is called 'cp'.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.
    nominal_power : float
        The nominal output of the wind power plant.
    wind_model : string, optional
        Chooses the model for calculating the wind speed at hub height.
        Used in v_wind_hub.
        Possibilities: 'logarithmic', 'logarithmic_closest' (The weather data
            set measured closest to hub height is used.).
    rho_model : string, optional
        Chooses the model for calculating the density of air at hub height.
        Used in rho_hub. Possibilities:'barometric', 'ideal_gas'.
    temperature_model : string, optional
        Chooses the model for calculating the temperature at hub height.
        Used in rho_hub. Possibilities: 'gradient', 'interpolation'.
    tp_output_model : string, optional
        Chooses the model for calculating the turbine power output.
        Used in turbine_power_output.
        Possibilities: 'cp_values', 'p_values', 'P_curve_correction'.
    density_corr : boolean, optional
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'd_rotor': 127,
    ...    'wind_conv_type': 'ENERCON E 126 7500'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> modelchain_data = {'rho_model': 'ideal_gas',
    ...    'temperature_model': 'interpolation'}
    >>> e126_md = modelchain.Modelchain(e126, **modelchain_data)
    >>> print(e126.d_rotor)
    127

    """

    def __init__(self, wind_turbine,
                 obstacle_height=0,
                 wind_model='logarithmic',
                 rho_model='barometric',
                 temperature_model='gradient',
                 tp_output_model='cp_values',
                 density_corr=False):

        self.wind_turbine = wind_turbine
        self.obstacle_height = obstacle_height

        # attributes
        self.hub_height = wind_turbine.hub_height
        self.d_rotor = wind_turbine.d_rotor
        self.cp_values = wind_turbine.cp_values
        self.p_values = wind_turbine.p_values
        self.nominal_power = wind_turbine.nominal_power

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
            (temp_air) and pressure (pressure).
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply.

        Other parameters
        ----------------
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for temperature
            (temp_air) and pressure (pressure).
        data_height_2 : dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air) and pressure (pressure).

        Returns
        -------
        rho_hub : pandas.Series or array
            Density of air in kg/m³ at hub height.

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
            (v_wind) and roughness length (z0).
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply.

        Other parameters
        ----------------
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            (v_wind) and roughness length (z0).
        data_height_2 : dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather_2` apply.

        Returns
        -------
        v_wind : pandas.Series or array
            Wind speed [m/s] at hub height as time series.

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

    def cp_series(self, v_wind):
        r"""
        Converts the curve of the power coefficient to a time series.

        Interpolates the power coefficient as a function of the wind speed
        between data obtained from the cp curve of the specified wind turbine
        type.

        Parameters
        ----------
        v_wind : pandas.Series or array
            Wind speed at hub height in m/s.

        Returns
        -------
        numpy.array
            Cp values for the wind speed time series.

        >>> import numpy
        >>> from windpowerlib import modelchain
        >>> e126 = modelchain.Modelchain('ENERCON E 126 7500')
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
            Containing columns or keys with the timeseries for temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0).
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply.

        Other parameters
        ----------------
        weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0).
        data_height_2 : dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather_2` apply.

        Returns
        -------
        pandas.Series
            Electrical power of the wind turbine.

        """
        # Calculation of parameters needed for power output
        v_wind = self.v_wind_hub(weather, data_height, **kwargs)
        rho_hub = self.rho_hub(weather, data_height, **kwargs)

        # Calculation of turbine power output according to the chosen model.
        if self.tp_output_model == 'cp_values':
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
            p_wpp = power_output.tpo_through_cp(v_wind, rho_hub, self.d_rotor,
                                                self.cp_series(v_wind))
        p_wpp_series = pd.Series(data=p_wpp,
                                 index=weather.index,
                                 name='feedin_wind_pp')
        p_wpp_series.index.names = ['']
        return p_wpp_series.clip(upper=(float(self.nominal_power)))

    def read_weather_data(self, filename, datetime_column='Unnamed: 0',
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

    def run_model(self, data_heights):
        r"""
        Runs the model.

        To run the model first a weather data set is read from a file.

        Parameters
        ----------
        data_heights : list or tuple of DataFrames or Dictionaries
            Contain columns or keys with the heights for which the
            corresponding parameters in of the weather data set apply.

        Returns
        -------
        self

        """
        # Loading weather data
        weather_df = self.read_weather_data('weather.csv')
        weather_df_2 = self.read_weather_data('weather_other_height.csv')

        self.wind_turbine.power_output = self.turbine_power_output(
            weather=weather_df, weather_2=weather_df_2,
            data_height=data_heights[0], data_height_2=data_heights[1])

        return self
