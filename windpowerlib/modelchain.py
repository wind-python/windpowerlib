"""
The ``modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and demonstrates standard ways to use the library.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import logging
from windpowerlib import (
    wind_speed,
    density,
    temperature,
    power_output,
    tools,
    data,
)


class ModelChain(object):
    r"""Model to determine the output of a wind turbine

    The ModelChain class provides a standardized, high-level
    interface for all of the modeling steps necessary for calculating wind
    turbine power output from weather time series inputs.

    Parameters
    ----------
    power_plant : :class:`~.wind_turbine.WindTurbine`
        A :class:`~.wind_turbine.WindTurbine` object representing the wind
        turbine.
    wind_speed_model : str
        Parameter to define which model to use to calculate the wind speed at
        hub height. Valid options are:

        * 'logarithmic' -
          See :func:`~.wind_speed.logarithmic_profile` for more information.
          The parameter `obstacle_height` can be used to set the height of
          obstacles in the surrounding area of the wind turbine.
        * 'hellman' -
          See :func:`~.wind_speed.hellman` for more information.
        * 'interpolation_extrapolation' -
          See :func:`~.tools.linear_interpolation_extrapolation` for more
          information.
        * 'log_interpolation_extrapolation' -
          See :func:`~.tools.logarithmic_interpolation_extrapolation` for more
          information.

        Default: 'logarithmic'.
    temperature_model : str
        Parameter to define which model to use to calculate the temperature of
        air at hub height. Valid options are:

        * 'linear_gradient' -
          See :func:`~.temperature.linear_gradient` for more
          information.
        * 'interpolation_extrapolation' -
          See :func:`~.tools.linear_interpolation_extrapolation` for more
          information.

        Default: 'linear_gradient'.
    density_model : str
        Parameter to define which model to use to calculate the density of air
        at hub height. Valid options are:

        * 'barometric' -
          See :func:`~.density.barometric` for more information.
        * 'ideal_gas' -
          See :func:`~.density.ideal_gas` for more information.
        * 'interpolation_extrapolation' -
          See :func:`~.tools.linear_interpolation_extrapolation` for more
          information.

        Default: 'barometric'.
    power_output_model : str
        Parameter to define which model to use to calculate the turbine power
        output. Valid options are:

        * 'power_curve' -
          See :func:`~.power_output.power_curve` for more information. In order
          to use the density corrected power curve to calculate the power
          output set parameter `density_correction` to True.
        * 'power_coefficient_curve' -
          See :func:`~.power_output.power_coefficient_curve` for more
          information.

        Default: 'power_curve'.
    density_correction : bool
        This parameter is only used if the parameter `power_output_model` is
        'power_curve'. For more information on this parameter see parameter
        `density_correction` in :func:`~.power_output.power_curve`.
        Default: False.
    obstacle_height : float
        This parameter is only used if the parameter `wind_speed_model` is
        'logarithmic'. For more information on this parameter see parameter
        `obstacle_height` in :func:`~.wind_speed.logarithmic`. Default: 0.
    hellman_exp : float
        This parameter is only used if the parameter `wind_speed_model` is
        'hellman'. For more information on this parameter see parameter
        `hellman_exponent` in :func:`~.wind_speed.hellman`. Default: None.

    Attributes
    ----------
    power_plant : :class:`~.wind_turbine.WindTurbine`
        A :class:`~.wind_turbine.WindTurbine` object representing the wind
        turbine.
    wind_speed_model : str
        Defines which model is used to calculate the wind speed at hub height.
    temperature_model : str
        Defines which model is used to calculate the temperature of air at hub
        height.
    density_model : str
        Defines which model is used to calculate the density of air at hub
        height.
    power_output_model : str
        Defines which model is used to calculate the turbine power output.
    density_correction : bool
        Used to set `density_correction` parameter in
        :func:`~.power_output.power_curve`.
    obstacle_height : float
        Used to set `obstacle_height` in :func:`~.wind_speed.logarithmic`.
    hellman_exp : float
        Used to set `hellman_exponent` in :func:`~.wind_speed.hellman`.
    power_output : :pandas:`pandas.Series<series>`
        Electrical power output of the wind turbine in W.

    Examples
    --------
    >>> from windpowerlib import modelchain
    >>> from windpowerlib import wind_turbine
    >>> enerconE126={
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'turbine_type': 'E-126/4200'}
    >>> e126=wind_turbine.WindTurbine(**enerconE126)
    >>> modelchain_data={'density_model': 'ideal_gas'}
    >>> e126_mc=modelchain.ModelChain(e126, **modelchain_data)
    >>> print(e126_mc.density_model)
    ideal_gas

    """

    def __init__(
        self,
        power_plant,
        wind_speed_model="logarithmic",
        temperature_model="linear_gradient",
        density_model="barometric",
        power_output_model="power_curve",
        density_correction=False,
        obstacle_height=0,
        hellman_exp=None,
        **kwargs,
    ):

        self.power_plant = power_plant
        self.obstacle_height = obstacle_height
        self.wind_speed_model = wind_speed_model
        self.temperature_model = temperature_model
        self.density_model = density_model
        self.power_output_model = power_output_model
        self.density_correction = density_correction
        self.hellman_exp = hellman_exp
        self.power_output = None

    def temperature_hub(self, weather_df):
        r"""
        Calculates the temperature of air at hub height.

        The temperature is calculated using the method specified by
        the parameter `temperature_model`.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for temperature `temperature` in K.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. temperature) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See documentation of
            :func:`ModelChain.run_model` for an example on how to create the
            weather_df DataFrame.

        Returns
        -------
        :pandas:`pandas.Series<series>` or numpy.array
            Temperature of air in K at hub height.

        Notes
        -----
        If `weather_df` contains temperatures at different heights the given
        temperature(s) closest to the hub height are used.

        """
        if self.power_plant.hub_height in weather_df["temperature"]:
            temperature_hub = weather_df["temperature"][
                self.power_plant.hub_height
            ]
        elif self.temperature_model == "linear_gradient":
            logging.debug(
                "Calculating temperature using temperature " "gradient."
            )
            closest_height = weather_df["temperature"].columns[
                min(
                    range(len(weather_df["temperature"].columns)),
                    key=lambda i: abs(
                        weather_df["temperature"].columns[i]
                        - self.power_plant.hub_height
                    ),
                )
            ]
            temperature_hub = temperature.linear_gradient(
                weather_df["temperature"][closest_height],
                closest_height,
                self.power_plant.hub_height,
            )
        elif self.temperature_model == "interpolation_extrapolation":
            logging.debug(
                "Calculating temperature using linear inter- or "
                "extrapolation."
            )
            temperature_hub = tools.linear_interpolation_extrapolation(
                weather_df["temperature"], self.power_plant.hub_height
            )
        else:
            raise ValueError(
                "'{0}' is an invalid value. ".format(self.temperature_model)
                + "`temperature_model` must be "
                "'linear_gradient' or 'interpolation_extrapolation'."
            )
        return temperature_hub

    def density_hub(self, weather_df):
        r"""
        Calculates the density of air at hub height.

        The density is calculated using the method specified by the parameter
        `density_model`. Previous to the calculation of the density the
        temperature at hub height is calculated using the method specified by
        the parameter `temperature_model`.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for temperature `temperature` in K,
            pressure `pressure` in Pa and/or density `density` in kg/m³,
            depending on the `density_model` used.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. temperature) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See documentation of
            :func:`ModelChain.run_model` for an example on how to create the
            weather_df DataFrame.

        Returns
        -------
        :pandas:`pandas.Series<series>` or numpy.array
            Density of air in kg/m³ at hub height.

        Notes
        -----
        If `weather_df` contains data at different heights the data closest to
        the hub height are used.
        If `interpolation_extrapolation` is used to calculate the density at
        hub height, the `weather_df` must contain at least two time series for
        density.
        """
        if self.density_model != "interpolation_extrapolation":
            temperature_hub = self.temperature_hub(weather_df)

        # Calculation of density in kg/m³ at hub height
        if self.density_model == "barometric":
            logging.debug(
                "Calculating density using barometric height " "equation."
            )
            closest_height = weather_df["pressure"].columns[
                min(
                    range(len(weather_df["pressure"].columns)),
                    key=lambda i: abs(
                        weather_df["pressure"].columns[i]
                        - self.power_plant.hub_height
                    ),
                )
            ]
            density_hub = density.barometric(
                weather_df["pressure"][closest_height],
                closest_height,
                self.power_plant.hub_height,
                temperature_hub,
            )
        elif self.density_model == "ideal_gas":
            logging.debug("Calculating density using ideal gas equation.")
            closest_height = weather_df["pressure"].columns[
                min(
                    range(len(weather_df["pressure"].columns)),
                    key=lambda i: abs(
                        weather_df["pressure"].columns[i]
                        - self.power_plant.hub_height
                    ),
                )
            ]
            density_hub = density.ideal_gas(
                weather_df["pressure"][closest_height],
                closest_height,
                self.power_plant.hub_height,
                temperature_hub,
            )
        elif self.density_model == "interpolation_extrapolation":
            logging.debug(
                "Calculating density using linear inter- or " "extrapolation."
            )
            density_hub = tools.linear_interpolation_extrapolation(
                weather_df["density"], self.power_plant.hub_height
            )
        else:
            raise ValueError(
                "'{0}' is an invalid value. ".format(self.density_model)
                + "`density_model` "
                + "must be 'barometric', 'ideal_gas' or "
                + "'interpolation_extrapolation'."
            )
        return density_hub

    def wind_speed_hub(self, weather_df):
        r"""
        Calculates the wind speed at hub height.

        The method specified by the parameter `wind_speed_model` is used.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for wind speed `wind_speed` in m/s and
            roughness length `roughness_length` in m.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. wind_speed) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See documentation of
            :func:`ModelChain.run_model` for an example on how to create the
            weather_df DataFrame.

        Returns
        -------
        :pandas:`pandas.Series<series>` or numpy.array
            Wind speed in m/s at hub height.

        Notes
        -----
        If `weather_df` contains wind speeds at different heights the given
        wind speed(s) closest to the hub height are used.

        """
        if self.power_plant.hub_height in weather_df["wind_speed"]:
            wind_speed_hub = weather_df["wind_speed"][
                self.power_plant.hub_height
            ]
        elif self.wind_speed_model == "logarithmic":
            logging.debug(
                "Calculating wind speed using logarithmic wind " "profile."
            )
            closest_height = weather_df["wind_speed"].columns[
                min(
                    range(len(weather_df["wind_speed"].columns)),
                    key=lambda i: abs(
                        weather_df["wind_speed"].columns[i]
                        - self.power_plant.hub_height
                    ),
                )
            ]
            wind_speed_hub = wind_speed.logarithmic_profile(
                weather_df["wind_speed"][closest_height],
                closest_height,
                self.power_plant.hub_height,
                weather_df["roughness_length"].iloc[:, 0],
                self.obstacle_height,
            )
        elif self.wind_speed_model == "hellman":
            logging.debug("Calculating wind speed using hellman equation.")
            closest_height = weather_df["wind_speed"].columns[
                min(
                    range(len(weather_df["wind_speed"].columns)),
                    key=lambda i: abs(
                        weather_df["wind_speed"].columns[i]
                        - self.power_plant.hub_height
                    ),
                )
            ]
            wind_speed_hub = wind_speed.hellman(
                weather_df["wind_speed"][closest_height],
                closest_height,
                self.power_plant.hub_height,
                weather_df["roughness_length"].iloc[:, 0],
                self.hellman_exp,
            )
        elif self.wind_speed_model == "interpolation_extrapolation":
            logging.debug(
                "Calculating wind speed using linear inter- or "
                "extrapolation."
            )
            wind_speed_hub = tools.linear_interpolation_extrapolation(
                weather_df["wind_speed"], self.power_plant.hub_height
            )
        elif self.wind_speed_model == "log_interpolation_extrapolation":
            logging.debug(
                "Calculating wind speed using logarithmic inter- or "
                "extrapolation."
            )
            wind_speed_hub = tools.logarithmic_interpolation_extrapolation(
                weather_df["wind_speed"], self.power_plant.hub_height
            )
        else:
            raise ValueError(
                "'{0}' is an invalid value. ".format(self.wind_speed_model)
                + "`wind_speed_model` must be "
                "'logarithmic', 'hellman', 'interpolation_extrapolation' "
                + "or 'log_interpolation_extrapolation'."
            )
        return wind_speed_hub

    def calculate_power_output(self, wind_speed_hub, density_hub):
        r"""
        Calculates the power output of the wind power plant.

        The method specified by the parameter `power_output_model` is used.

        Parameters
        ----------
        wind_speed_hub : :pandas:`pandas.Series<series>` or numpy.array
            Wind speed at hub height in m/s.
        density_hub : :pandas:`pandas.Series<series>` or numpy.array
            Density of air at hub height in kg/m³.

        Returns
        -------
        :pandas:`pandas.Series<series>`
            Electrical power output of the wind turbine in W.

        """
        if self.power_output_model == "power_curve":
            if self.power_plant.power_curve is None:
                raise TypeError(
                    "Power curve values of {} are missing.".format(
                        self.power_plant
                    )
                )
            logging.debug("Calculating power output using power curve.")
            return power_output.power_curve(
                wind_speed_hub,
                self.power_plant.power_curve["wind_speed"],
                self.power_plant.power_curve["value"],
                density_hub,
                self.density_correction,
            )
        elif self.power_output_model == "power_coefficient_curve":
            if self.power_plant.power_coefficient_curve is None:
                raise TypeError(
                    "Power coefficient curve values of {} are "
                    "missing.".format(self.power_plant)
                )
            logging.debug(
                "Calculating power output using power coefficient " "curve."
            )
            return power_output.power_coefficient_curve(
                wind_speed_hub,
                self.power_plant.power_coefficient_curve["wind_speed"],
                self.power_plant.power_coefficient_curve["value"],
                self.power_plant.rotor_diameter,
                density_hub,
            )
        else:
            raise ValueError(
                "'{0}' is an invalid value. ".format(self.power_output_model)
                + "`power_output_model` must be "
                + "'power_curve' or 'power_coefficient_curve'."
            )

    def run_model(self, weather_df):
        r"""
        Runs the model.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for wind speed `wind_speed` in m/s, and
            roughness length `roughness_length` in m, as well as optionally
            temperature `temperature` in K, pressure `pressure` in Pa and
            density `density` in kg/m³ depending on `power_output_model` and
            `density_model chosen`.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. wind_speed) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See below for an example on how to
            create the weather_df DataFrame.

        Returns
        -------
        :class:`~.modelchain.ModelChain`

        Examples
        ---------
        >>> import numpy as np
        >>> import pandas as pd
        >>> my_weather_df = pd.DataFrame(np.random.rand(2,6),
        ...                           index=pd.date_range('1/1/2012',
        ...                                               periods=2,
        ...                                               freq='H'),
        ...                           columns=[np.array(['wind_speed',
        ...                                              'wind_speed',
        ...                                              'temperature',
        ...                                              'temperature',
        ...                                              'pressure',
        ...                                              'roughness_length']),
        ...                                    np.array([10, 80, 10, 80,
        ...                                             10, 0])])
        >>> my_weather_df.columns.get_level_values(0)[0]
        'wind_speed'

        """
        weather_df = data.check_weather_data(weather_df)

        wind_speed_hub = self.wind_speed_hub(weather_df)
        density_hub = (
            None
            if (
                self.power_output_model == "power_curve"
                and self.density_correction is False
            )
            else self.density_hub(weather_df)
        )
        self.power_output = self.calculate_power_output(
            wind_speed_hub, density_hub
        )
        return self
