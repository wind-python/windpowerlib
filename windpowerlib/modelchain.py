"""
The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
from windpowerlib import wind_speed, density, power_output, tools
import pandas as pd


class ModelChain(object):
    r"""Model to determine the output of a wind turbine

    Parameters
    ----------
    wind_turbine : WindTurbine
        A :class:`~.wind_turbine.WindTurbine` object representing the wind
        turbine.
    obstacle_height : float
        Height of obstacles in the surrounding area of the wind turbine in m.
        Set `obstacle_height` to zero for wide spread obstacles. Default: 0.
    wind_model : string
        Parameter to define which model to use to calculate the wind speed at
        hub height. Valid options are 'logarithmic' and 'hellman'.
        Default: 'logarithmic'.
    rho_model : string
        Parameter to define which model to use to calculate the density of air
        at hub height. Valid options are 'barometric' and 'ideal_gas'.
        Default: 'barometric'.
    power_output_model : string
        Parameter to define which model to use to calculate the turbine power
        output. Valid options are 'cp_values' and 'p_values'.
        Default: 'p_values'.
    density_corr : boolean
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False.
    hellman_exp : float
        The Hellman exponent, which combines the increase in wind speed due to
        stability of atmospheric conditions and surface roughness into one
        constant. Default: None.

    Attributes
    ----------
    wind_turbine : WindTurbine
        A :class:`~.wind_turbine.WindTurbine` object representing the wind
        turbine.
    obstacle_height : float
        Height of obstacles in the surrounding area of the wind turbine in m.
        Set `obstacle_height` to zero for wide spread obstacles. Default: 0.
    wind_model : string
        Parameter to define which model to use to calculate the wind speed at
        hub height. Valid options are 'logarithmic' and 'hellman'.
        Default: 'logarithmic'.
    rho_model : string
        Parameter to define which model to use to calculate the density of air
        at hub height. Valid options are 'barometric' and 'ideal_gas'.
        Default: 'barometric'.
    power_output_model : string
        Parameter to define which model to use to calculate the turbine power
        output. Valid options are 'cp_values' and 'p_values'.
        Default: 'p_values'.
    density_corr : boolean
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False.
    hellman_exp : float
        The Hellman exponent, which combines the increase in wind speed due to
        stability of atmospheric conditions and surface roughness into one
        constant. Default: None.
    power_output : pandas.Series
        Electrical power output of the wind turbine in W.

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> from windpowerlib import wind_turbine
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'turbine_name': 'ENERCON E 126 7500'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> modelchain_data = {'rho_model': 'ideal_gas'}
    >>> e126_md = modelchain.ModelChain(e126, **modelchain_data)
    >>> print(e126.rotor_diameter)
    127

    """

    def __init__(self, wind_turbine,
                 obstacle_height=0,
                 wind_model='logarithmic',
                 temp_model='temperature_gradient',
                 rho_model='barometric',
                 power_output_model='p_values',
                 density_corr=False,
                 hellman_exp=None):

        self.wind_turbine = wind_turbine
        self.obstacle_height = obstacle_height
        self.wind_model = wind_model
        self.temp_model = temp_model
        self.rho_model = rho_model
        self.power_output_model = power_output_model
        self.density_corr = density_corr
        self.hellman_exp = hellman_exp
        self.power_output = None

    def rho_hub(self, weather):
        r"""
        Calculates the density of air at hub height.

        The density is calculated using the method specified by the parameter
        `rho_model`. Previous to the calculation of density the temperature at
        hub height is calculated using a linear temperature gradient.

        Parameters
        ----------
        weather : pandas.DataFrame or Dictionary
            Containing columns or keys with timeseries for temperature
            `temp_air` in K and pressure `pressure` in Pa, as well as
            optionally the temperature `temp_air_2` in K at a different height.
            If a Dictionary is used the data inside the dictionary has to be of
            the types pandas.Series or numpy.array.

        Returns
        -------
        rho_hub : pandas.Series or numpy.array
            Density of air in kg/m³ at hub height.

        """
        try:
            temp_hub = weather['temp'][self.wind_turbine.hub_height]
        except:
            if self.temp_model == 'temperature_gradient':
                logging.debug('Calculating temperature using temperature'
                              'gradient.')
                closest_height = weather['temp_air'].columns[
                    min(range(len(weather['temp_air'].columns)),
                        key=lambda i: abs(weather['temp_air'].columns[i] -
                                          self.wind_turbine.hub_height))]
                temp_hub = density.temperature_gradient(
                    weather['temp_air'][closest_height], closest_height,
                    self.obstacle_height)
            elif self.temp_model == 'linear':
                logging.debug('Calculating wind using linear inter- or'
                              'extrapolation.')
                temp_hub = tools.linear_extra_interpolation(
                    weather['temp_air'], self.wind_turbine.hub_height)
            else:
                raise ValueError("'{0}' is an invalid value.".format(
                    self.wind_model) + "`wind_model` must be 'logarithmic',"
                    "'hellman' or 'linear'.")

        # Calculation of density in kg/m³ at hub height
        if self.rho_model == 'barometric':
            logging.debug('Calculating density using barometric height'
                          'equation.')
            closest_height = weather['pressure'].columns[
                min(range(len(weather['pressure'].columns)),
                    key=lambda i: abs(weather['pressure'].columns[i] -
                                      self.wind_turbine.hub_height))]
            rho_hub = density.rho_barometric(
                weather['pressure'][closest_height], closest_height,
                self.wind_turbine.hub_height, temp_hub)
        elif self.rho_model == 'ideal_gas':
            logging.debug('Calculating density using ideal gas equation.')
            closest_height = weather['pressure'].columns[
                min(range(len(weather['pressure'].columns)),
                    key=lambda i: abs(weather['pressure'].columns[i] -
                                      self.wind_turbine.hub_height))]
            rho_hub = density.rho_ideal_gas(
                weather['pressure'][closest_height], closest_height,
                self.wind_turbine.hub_height, temp_hub)
        elif self.rho_model == 'linear':
            logging.debug('Calculating density using linear inter- or'
                          'extrapolation.')
            rho_hub = tools.linear_extra_interpolation(
                weather['density'], self.wind_turbine.hub_height)
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.rho_model) + "`rho_model` " +
                             "must be 'barometric', 'ideal_gas' or 'linear'.")
        return rho_hub

    def v_wind_hub(self, weather):
        r"""
        Calculates the wind speed at hub height.

        The method specified by the parameter `wind_model` is used.

        Parameters
        ----------
        weather : pandas.DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            `v_wind` in m/s and roughness length `z0` in m, as well as
            optionally wind speed `v_wind_2` in m/s at different height.
            If a Dictionary is used the data inside the dictionary has to be of
            the types pandas.Series or numpy.array.

        Returns
        -------
        v_wind : pandas.Series or numpy.array
            Wind speed in m/s at hub height.

        Notes
        -----
        If `weather` contains wind speeds at different heights it is calculated
        with `v_wind` of which data height is closer to hub height.

        """
        try:
            v_wind = weather['v_wind'][self.wind_turbine.hub_height]
        except:
            if self.wind_model == 'logarithmic':
                logging.debug('Calculating wind speed using logarithmic wind'
                              'profile.')
                closest_height = weather['v_wind'].columns[
                    min(range(len(weather['v_wind'].columns)),
                        key=lambda i: abs(weather['v_wind'].columns[i] -
                                          self.wind_turbine.hub_height))]
                v_wind = wind_speed.logarithmic_wind_profile(
                    weather['v_wind'][closest_height], closest_height,
                    self.wind_turbine.hub_height, weather['z0'].ix[:,0],
                    self.obstacle_height)
            elif self.wind_model == 'hellman':
                logging.debug('Calculating windspeed using hellman equation.')
                closest_height = weather['v_wind'].columns[
                    min(range(len(weather['v_wind'].columns)),
                        key=lambda i: abs(weather['v_wind'].columns[i] -
                                          self.wind_turbine.hub_height))]
                v_wind = wind_speed.v_wind_hellman(
                    weather['v_wind'][closest_height], closest_height,
                    self.wind_turbine.hub_height, weather['z0'].ix[:,0],
                    self.hellman_exp)
            elif self.wind_model == 'linear':
                logging.debug('Calculating wind speed using linear inter- or'
                              'extrapolation.')
                v_wind = tools.linear_extra_interpolation(
                    weather['v_wind'], self.wind_turbine.hub_height)
            else:
                raise ValueError("'{0}' is an invalid value.".format(
                    self.wind_model) + "`wind_model` must be 'logarithmic',"
                    "'hellman' or 'linear'.")

        return v_wind

    def turbine_power_output(self, wind_speed, density):
        r"""
        Calculates the power output of the wind turbine.

        The method specified by the parameter `power_output_model` is used.

        Parameters
        ----------
        wind_speed : pandas.Series or numpy.array
            Wind speed at hub height in m/s.
        density : pandas.Series or numpy.array
            Density of air at hub height in kg/m³.

        Returns
        -------
        output : pandas.Series
            Electrical power output of the wind turbine in W.

        """
        if self.power_output_model == 'cp_values':
            if self.wind_turbine.cp_values is None:
                raise TypeError("Cp values of " +
                                self.wind_turbine.turbine_name +
                                " are missing.")
            logging.debug('Calculating power output using cp curve.')
            output = power_output.power_coefficient_curve(
                wind_speed, self.wind_turbine.cp_values,
                self.wind_turbine.rotor_diameter, density,
                self.density_corr)
        elif self.power_output_model == 'p_values':
            if self.wind_turbine.p_values is None:
                raise TypeError("P values of " +
                                self.wind_turbine.turbine_name +
                                " are missing.")
            logging.debug('Calculating power output using power curve.')
            output = power_output.power_curve(
                wind_speed, self.wind_turbine.p_values, density,
                self.density_corr)
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.power_output_model) +
                             "`power_output_model` " +
                             "must be 'cp_values' or 'p_values'.")
        return output

    def run_model(self, weather):
        r"""
        Runs the model.

        Parameters
        ----------
        weather : pandas.DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            `v_wind` in m/s, roughness length `z0` in m, temperature
            `temp_air` in K and pressure `pressure` in Pa, as well as
            optionally wind speed `v_wind_2` in m/s and temperature
            `temp_air_2` in K at different height.
            If a Dictionary is used the data inside the dictionary has to be of
            the types pandas.Series or numpy.array.

        Returns
        -------
        self

        """
        wind_speed = self.v_wind_hub(weather)
        density = (None if (self.power_output_model == 'p_values' and
                   self.density_corr is False)
                   else self.rho_hub(weather))
        self.power_output = self.turbine_power_output(wind_speed, density)
        return self
