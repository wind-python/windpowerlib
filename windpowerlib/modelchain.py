"""
The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

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
        set measured closest to hub height is used.), 'hellman'.
    rho_model : string, optional
        Chooses the model for calculating the density of air at hub height.
        Used in rho_hub. Possibilities:'barometric', 'ideal_gas'.
    temperature_model : string, optional
        Chooses the model for calculating the temperature at hub height.
        Used in rho_hub. Possibilities: 'gradient', 'interpolation'.
    power_output_model : string, optional
        Chooses the model for calculating the turbine power output.
        Used in turbine_power_output.
        Possibilities: 'cp_values', 'p_values', 'P_curve_correction'.
    density_corr : boolean, optional
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False
    hellman_exp : float
        The Hellman exponent, which combines the increase in wind speed due to
        stability of atmospheric conditions and surface roughness into one
        constant. Default: None.
    hellman_z0 : float
        Roughness length. Default: None.

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
        set measured closest to hub height is used.), 'hellman'.
    rho_model : string, optional
        Chooses the model for calculating the density of air at hub height.
        Used in rho_hub. Possibilities:'barometric', 'ideal_gas'.
    temperature_model : string, optional
        Chooses the model for calculating the temperature at hub height.
        Used in rho_hub. Possibilities: 'gradient', 'interpolation'.
    power_output_model : string, optional
        Chooses the model for calculating the turbine power output.
        Used in turbine_power_output.
        Possibilities: 'cp_values', 'p_values', 'P_curve_correction'.
    density_corr : boolean, optional
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False
    hellman_exp : float
        The Hellman exponent, which combines the increase in wind speed due to
        stability of atmospheric conditions and surface roughness into one
        constant. Default: None.
    hellman_z0 : float
        Roughness length. Default: None.

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
                 power_output_model='cp_values',
                 density_corr=False,
                 hellman_exp=None,
                 hellman_z0=None):

        self.wind_turbine = wind_turbine
        self.obstacle_height = obstacle_height

        # call models
        self.wind_model = wind_model
        self.rho_model = rho_model
        self.temperature_model = temperature_model
        self.power_output_model = power_output_model
        self.density_corr = density_corr
        self.hellman_exp = hellman_exp
        self.hellman_z0 = hellman_z0

    def rho_hub(self, weather, data_height):
        r"""
        Calculates the density of air at hub height.

        Within the function the temperature at hub height is calculated as
        well if it is not given at hub height.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for temperature
            (temp_air) and pressure (pressure). Optional temperature at
            different height (temp_air_2) for interpolation.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        rho_hub : pandas.Series or array
            Density of air in kg/m³ at hub height.

        """
        # Check if temperature data is at hub height.
        if data_height['temp_air'] == self.wind_turbine.hub_height:
            logging.debug('Using given temperature (at hub height).')
            T_hub = weather['temp_air']
        # Calculation of temperature in K at hub height according to the
        # chosen model.
        elif self.temperature_model == 'gradient':
            logging.debug('Calculating temperature with gradient.')
            T_hub = density.temperature_gradient(
                weather['temp_air'], data_height['temp_air'],
                self.wind_turbine.hub_height)
        elif self.temperature_model == 'interpolation':
            if 'temp_air_2' not in weather or 'temp_air_2' not in data_height:
                logging.info('One temperature or data height is missing. It ' +
                             'was calculated with a temperature gradient.')
                T_hub = density.temperature_gradient(
                    weather['temp_air'], data_height['temp_air'],
                    self.hub_height)
            # Check if temperature data of second data set is at hub height.
            elif data_height['temp_air_2'] == self.hub_height:
                logging.debug('Using given temperature (at hub height).')
                T_hub = weather['temp_air_2']
            else:
                logging.debug('Calculating temperature with interpolation.')
                T_hub = density.temperature_interpol(
                    weather['temp_air'], weather['temp_air_2'],
                    data_height['temp_air'], data_height['temp_air_2'],
                    self.hub_height)
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
                                             self.wind_turbine.hub_height,
                                             T_hub)
        elif self.rho_model == 'ideal_gas':
            logging.debug('Calculating density with ideal gas equation.')
            rho_hub = density.rho_ideal_gas(weather['pressure'],
                                            data_height['pressure'],
                                            self.wind_turbine.hub_height,
                                            T_hub)
        else:
            logging.info('wrong value: `rho_model` must be barometric ' +
                         'or ideal_gas. It was calculated with barometric.')
            rho_hub = density.rho_barometric(weather['pressure'],
                                             data_height['pressure'],
                                             self.hub_height, T_hub)
        return rho_hub

    def v_wind_hub(self, weather, data_height):
        r"""
        Calculates the wind speed at hub height.

        The method specified by the parameter `wind_model` is used.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            `v_wind` in m/s and roughness length `z0` in m, as well as
            optionally wind speed `v_wind_2` in m/s at different height for
            interpolation.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights in m for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        v_wind : pandas.Series or array
            Wind speed in m/s at hub height.

        """
        # Check if wind speed data is at hub height.
        if 'v_wind_2' not in weather:
            weather['v_wind_2'] = None
            data_height['v_wind_2'] = None
        if data_height['v_wind'] == self.wind_turbine.hub_height:
            logging.debug('Using given wind speed (at hub height).')
            v_wind = weather['v_wind']
        elif data_height['v_wind_2'] == self.wind_turbine.hub_height:
            logging.debug('Using given wind speed (2) (at hub height).')
            v_wind = weather['v_wind_2']
        # Calculation of wind speed in m/s at hub height.
        elif self.wind_model == 'logarithmic':
            logging.debug('Calculating v_wind using logarithmic wind profile.')
            if weather['v_wind_2'] is None:
                v_wind = wind_speed.logarithmic_wind_profile(
                    weather['v_wind'], data_height['v_wind'],
                    self.wind_turbine.hub_height,
                    weather['z0'], self.obstacle_height)
            else:
                if (abs(data_height['v_wind'] -
                        self.wind_turbine.hub_height) <=
                        abs(data_height['v_wind_2'] -
                            self.wind_turbine.hub_height)):
                    v_wind = wind_speed.logarithmic_wind_profile(
                        weather['v_wind'], data_height['v_wind'],
                        self.wind_turbine.hub_height, weather['z0'],
                        self.obstacle_height)
                else:
                    v_wind = wind_speed.logarithmic_wind_profile(
                        weather['v_wind_2'], data_height['v_wind_2'],
                        self.wind_turbine.hub_height, weather['z0'],
                        self.obstacle_height)
        elif self.wind_model == 'hellman':
            logging.debug('Calculating v_wind using hellman equation.')
            v_wind = wind_speed.v_wind_hellman(
                weather['v_wind'], data_height['v_wind'],
                self.wind_turbine.hub_height,
                self.hellman_exp, self.hellman_z0)
        else:
            logging.error('Wrong value: `wind_model` must be logarithmic ' +
                          'or hellman.')
            sys.exit()
        return v_wind

    def turbine_power_output(self, v_wind, rho_hub):
        r"""
        Calculates the power output of the wind turbine.

        The method specified by the parameter `power_output_model` is used.

        Parameters
        ----------
        v_wind : pandas.Series or array
            Wind speed at hub height in m/s.
        rho_hub : pandas.Series or array
            Density of air at hub height in kg/m³.

        Returns
        -------
        output : pandas.Series
            Electrical power in W of the wind turbine.

        """
        if self.power_output_model == 'cp_values':
            if self.density_corr is False:
                logging.debug('Calculating power output using cp curve.')
                output = power_output.cp_curve(v_wind, rho_hub,
                                               self.wind_turbine.d_rotor,
                                               self.wind_turbine.cp_values)
            else:
                logging.debug('Calculating power output using density ' +
                              'corrected cp curve.')
                output = power_output.cp_curve_density_corr(
                    v_wind, rho_hub, self.wind_turbine.d_rotor,
                    self.wind_turbine.cp_values)
        elif self.power_output_model == 'p_values':
            if self.density_corr is False:
                logging.debug('Calculating power output using power curve.')
                output = power_output.p_curve(self.wind_turbine.p_values,
                                              v_wind)
            else:
                logging.debug('Calculating power output using density ' +
                              'corrected power curve.')
                output = power_output.p_curve_density_corr(
                    v_wind, rho_hub, self.wind_turbine.p_values)
        else:
            logging.info('Wrong value: `power_output_model` must be ' +
                         'cp_values or p_values.')
        return output

    def run_model(self, weather, data_height):
        r"""
        Runs the model.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            `v_wind` in m/s ,roughness length `z0` in m, temperature
            `temp_air` in K and pressure `pressure` in Pa, as well as
            optionally wind speed `v_wind_2` in m/s and temperature
            `temp_air_2` in K at different height for interpolation.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights in m for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        self

        """
        v_wind = self.v_wind_hub(weather, data_height)
        rho_hub = self.rho_hub(weather, data_height)
        self.power_output = self.turbine_power_output(v_wind, rho_hub)
        return self
