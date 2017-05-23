"""
The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import logging
from windpowerlib import wind_speed, density, power_output


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
    temperature_model : string
        Parameter to define which model to use to calculate the temperature at
        hub height. Valid options are 'gradient' and 'interpolation'.
        Default: 'gradient'.
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
    temperature_model : string
        Parameter to define which model to use to calculate the temperature at
        hub height. Valid options are 'gradient' and 'interpolation'.
        Default: 'gradient'.
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
    ...    'd_rotor': 127,
    ...    'wind_conv_type': 'ENERCON E 126 7500'}
    >>> e126 = wind_turbine.WindTurbine(**enerconE126)
    >>> modelchain_data = {'rho_model': 'ideal_gas',
    ...    'temperature_model': 'interpolation'}
    >>> e126_md = modelchain.ModelChain(e126, **modelchain_data)
    >>> print(e126.d_rotor)
    127

    """

    def __init__(self, wind_turbine,
                 obstacle_height=0,
                 wind_model='logarithmic',
                 rho_model='barometric',
                 temperature_model='gradient',
                 power_output_model='p_values',
                 density_corr=False,
                 hellman_exp=None):

        self.wind_turbine = wind_turbine
        self.obstacle_height = obstacle_height
        self.wind_model = wind_model
        self.rho_model = rho_model
        self.temperature_model = temperature_model
        self.power_output_model = power_output_model
        self.density_corr = density_corr
        self.hellman_exp = hellman_exp
        self.power_output = None

    def rho_hub(self, weather, data_height):
        r"""
        Calculates the density of air at hub height.

        The density is calculated using the method specified by the parameter
        `rho_model`. Previous to the calculation of density the temperature at
        hub height is calculated using the method specified by the parameter
        `temperature_model`.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with timeseries for temperature
            `temp_air` in K and pressure `pressure` in Pa, as well as
            optionally the temperature `temp_air_2` in K at a different height
            for interpolation.
            Data inside the Dictionary has to be of the types pandas.Series or
            numpy.array.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights in m for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        rho_hub : pandas.Series or array
            Density of air in kg/m³ at hub height.

        """
        # Check if temperature data is at hub height.
        if 'temp_air_2' not in weather:
            weather['temp_air_2'] = None
            data_height['temp_air_2'] = None
        if data_height['temp_air'] == self.wind_turbine.hub_height:
            logging.debug('Using given temperature (at hub height).')
            temp_hub = weather['temp_air']
        elif data_height['temp_air_2'] == self.wind_turbine.hub_height:
            logging.debug('Using given temperature (2) (at hub height).')
            temp_hub = weather['temp_air_2']
        # Calculation of temperature in K at hub height.
        elif self.temperature_model == 'gradient':
            logging.debug('Calculating temperature using a temp. gradient.')
            temp_hub = density.temperature_gradient(
                weather['temp_air'], data_height['temp_air'],
                self.wind_turbine.hub_height)
        elif self.temperature_model == 'interpolation':
            logging.debug('Calculating temperature using interpolation.')
            temp_hub = density.temperature_interpol(
                weather['temp_air'], weather['temp_air_2'],
                data_height['temp_air'], data_height['temp_air_2'],
                self.wind_turbine.hub_height)
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.temperature_model) + "`temperature_model` " +
                             "must be 'gradient' or 'interpolation'.")
        # Calculation of density in kg/m³ at hub height
        if self.rho_model == 'barometric':
            logging.debug('Calculating density using barometric height eq.')
            rho_hub = density.rho_barometric(weather['pressure'],
                                             data_height['pressure'],
                                             self.wind_turbine.hub_height,
                                             temp_hub)
        elif self.rho_model == 'ideal_gas':
            logging.debug('Calculating density using ideal gas equation.')
            rho_hub = density.rho_ideal_gas(weather['pressure'],
                                            data_height['pressure'],
                                            self.wind_turbine.hub_height,
                                            temp_hub)
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.rho_model) + "`rho_model` " +
                             "must be 'barometric' or 'ideal_gas'.")
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
            optionally wind speed `v_wind_2` in m/s at different height.
            Data inside the Dictionary has to be of the types pandas.Series or
            numpy.array.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights in m for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        v_wind : pandas.Series or array
            Wind speed in m/s at hub height.

        Notes
        -----
        If `weather` contains wind speeds at different heights it is calculated
        with `v_wind` of which data height is closer to hub height.

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
            if weather['v_wind_2'].isnull().all():
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
                self.hellman_exp, weather['z0'])
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.wind_model) + "`wind_model` " +
                             "must be 'logarithmic' or 'hellman'.")
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
            if self.wind_turbine.cp_values is None:
                raise TypeError("Cp values of " +
                                self.wind_turbine.turbine_name +
                                " are missing.")
            if self.density_corr is False:
                logging.debug('Calculating power output using cp curve.')
                output = power_output.cp_curve(v_wind, rho_hub,
                                               self.wind_turbine.d_rotor,
                                               self.wind_turbine.cp_values)
            elif self.density_corr is True:
                logging.debug('Calculating power output using density ' +
                              'corrected cp curve.')
                output = power_output.cp_curve_density_corr(
                    v_wind, rho_hub, self.wind_turbine.d_rotor,
                    self.wind_turbine.cp_values)
            else:
                raise TypeError("'{0}' is an invalid type.".format(type(
                                self.density_corr)) + "`density_corr` must " +
                                "be Boolean (True or False).")
        elif self.power_output_model == 'p_values':
            if self.wind_turbine.p_values is None:
                raise TypeError("P values of " +
                                self.wind_turbine.turbine_name +
                                " are missing.")
            if self.density_corr is False:
                logging.debug('Calculating power output using power curve.')
                output = power_output.p_curve(self.wind_turbine.p_values,
                                              v_wind)
            elif self.density_corr is True:
                logging.debug('Calculating power output using density ' +
                              'corrected power curve.')
                output = power_output.p_curve_density_corr(
                    v_wind, rho_hub, self.wind_turbine.p_values)
            else:
                raise TypeError("'{0}' is an invalid type.".format(type(
                                self.density_corr)) + "`density_corr` must " +
                                "be Boolean (True or False).")
        else:
            raise ValueError("'{0}' is an invalid value.".format(
                             self.power_output_model) +
                             "`power_output_model` " +
                             "must be 'cp_values' or 'p_values'.")
        return output

    def run_model(self, weather, data_height):
        r"""
        Runs the model.

        Parameters
        ----------
        weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for wind speed
            `v_wind` in m/s, roughness length `z0` in m, temperature
            `temp_air` in K and pressure `pressure` in Pa, as well as
            optionally wind speed `v_wind_2` in m/s and temperature
            `temp_air_2` in K at different height for interpolation.
            Data inside the Dictionary has to be of the types pandas.Series or
            numpy.array.
        data_height : DataFrame or Dictionary
            Containing columns or keys with the heights in m for which the
            corresponding parameters in `weather` apply.

        Returns
        -------
        self

        """
        v_wind = self.v_wind_hub(weather, data_height)
        rho_hub = None if (self.power_output_model == 'p_values' and
                           self.density_corr is False) \
                       else self.rho_hub(weather, data_height)
        self.power_output = self.turbine_power_output(v_wind, rho_hub)
        return self
