"""
The ``turbine_cluster_modelchain`` module contains functions and classes of the
windpowerlib. This module makes it easy to get started with the windpowerlib
and shows use cases for the power output calculation of wind farms and wind
turbine clusters.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import logging
from windpowerlib import wake_losses
from windpowerlib.modelchain import ModelChain, data


class TurbineClusterModelChain(ModelChain):
    r"""
    Model to determine the output of a wind farm or wind turbine cluster.

    Parameters
    ----------
    power_plant : :class:`~.wind_farm.WindFarm` or :class:`~.wind_turbine_cluster.WindTurbineCluster`
        A :class:`~.wind_farm.WindFarm` object representing the wind farm or
        a :class:`~.wind_turbine_cluster.WindTurbineCluster` object
        representing the wind turbine cluster.
    wake_losses_model : str or None
        Defines the method for taking wake losses within the farm into
        consideration.

        * None -
          Wake losses are not taken into account.
        * 'wind_farm_efficiency' -
          The values of the wind farm power curve(s) are reduced by the wind
          farm efficiency, which needs to be set in the
          :py:class:`~.wind_farm.WindFarm` class. Note: The wind farm
          efficiency has no effect if `wake_losses_model` is not set to
          'wind_farm_efficiency'.
          See :func:`~.power_curves.wake_losses_to_power_curve` for more
          information.
        * 'dena_mean' or name of other wind efficiency curve -
          The values of the wind speed time series are reduced by the chosen
          wind efficiency curve in :func:`~.run_model` before the power output
          calculations.
          See :func:`~.wake_losses.reduce_wind_speed` for more information.
          Use :func:`~.wake_losses.get_wind_efficiency_curve` to get a
          DataFrame of all provided wind efficiency curves and see the provided
          example on how to plot the wind efficiency curves.
          
       Default: 'dena_mean'.
    smoothing : bool
        If True the power curves will be smoothed to account for the
        distribution of wind speeds over space. Depending on the parameter
        `smoothing_order` the power curves are smoothed before or after
        aggregating wind turbine power curves to one representative power
        curve of the wind farm or cluster.
        See :func:`~.power_curves.smooth_power_curve` for more information.

        Default: False.
    block_width : float
        Width between the wind speeds in the sum of the equation in
        :py:func:`~.power_curves.smooth_power_curve`. This parameter is only
        used if `smoothing` is True. To achieve a smooth curve without steps a
        value not much higher than the step width between the power curve wind
        speeds should be chosen.

        Default: 0.5.
    standard_deviation_method : str
        Method for calculating the standard deviation for the Gauss
        distribution if `smoothing` is True.

        * 'turbulence_intensity' -
          See :func:`~.power_curves.smooth_power_curve` for more information.
        * 'Staffell_Pfenninger' -
          See :func:`~.power_curves.smooth_power_curve` for more information.

        Default: 'turbulence_intensity'.
    smoothing_order : str
        Defines when the smoothing takes place if `smoothing` is True.

        * 'turbine_power_curves' -
          Smoothing is applied to wind turbine power curves.
        * 'wind_farm_power_curves' -
          Smoothing is applied to wind farm power curves.

        Default: 'wind_farm_power_curves'.

    Other Parameters
    ----------------
    wind_speed_model :
        See :py:class:`~.modelchain.ModelChain` for more information.
    temperature_model :
        See :py:class:`~.modelchain.ModelChain` for more information.
    density_model :
        See :py:class:`~.modelchain.ModelChain` for more information.
    power_output_model :
        See :py:class:`~.modelchain.ModelChain` for more information.
    density_correction :
        See :py:class:`~.modelchain.ModelChain` for more information.
    obstacle_height :
        See :py:class:`~.modelchain.ModelChain` for more information.
    hellman_exp :
        See :py:class:`~.modelchain.ModelChain` for more information.

    Attributes
    ----------
    power_plant : :class:`~.wind_farm.WindFarm` or :class:`~.wind_turbine_cluster.WindTurbineCluster`
        A :class:`~.wind_farm.WindFarm` object representing the wind farm or
        a :class:`~.wind_turbine_cluster.WindTurbineCluster` object
        representing the wind turbine cluster.
    wake_losses_model : str or None
        Defines the method for taking wake losses within the farm into
        consideration.
    smoothing : bool
        If True the power curves are smoothed.
    block_width : float
        Width between the wind speeds in the sum of the equation in
        :py:func:`~.power_curves.smooth_power_curve`.
    standard_deviation_method : str
        Method for calculating the standard deviation for the Gauss
        distribution.
    smoothing_order : str
        Defines when the smoothing takes place if `smoothing` is True.
    power_output : :pandas:`pandas.Series<series>`
        Electrical power output of the wind turbine in W.
    power_curve : :pandas:`pandas.Dataframe<frame>` or None
        The calculated power curve of the wind farm.
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

    """

    def __init__(
        self,
        power_plant,
        wake_losses_model="dena_mean",
        smoothing=False,
        block_width=0.5,
        standard_deviation_method="turbulence_intensity",
        smoothing_order="wind_farm_power_curves",
        **kwargs,
    ):
        super(TurbineClusterModelChain, self).__init__(power_plant, **kwargs)

        self.power_plant = power_plant
        self.wake_losses_model = wake_losses_model
        self.smoothing = smoothing
        self.block_width = block_width
        self.standard_deviation_method = standard_deviation_method
        self.smoothing_order = smoothing_order

        self.power_curve = None
        self.power_output = None

    def assign_power_curve(self, weather_df):
        r"""
        Calculates the power curve of the wind turbine cluster.

        The power curve is aggregated from the wind farms' and wind turbines'
        power curves by using :func:`power_plant.assign_power_curve`. Depending
        on the parameters of the WindTurbineCluster power curves are smoothed
        and/or wake losses are taken into account.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with weather data time series. If power curve smoothing
            :py:attr:`~smoothing` is True and chosen method for calculating the
            standard deviation :py:attr:`~standard_deviation_method` is
            `turbulence_intensity` the weather dataframe needs to either
            contain the turbulence intensity in column 'turbulence_intensity'
            or the roughness length in m in column 'roughness_length'. The
            turbulence intensity should be provided at hub height or at least
            at a height close to the hub height, as it cannot be inter- or
            extrapolated.

        Returns
        -------
        self

        """
        # Get turbulence intensity from weather if existent
        turbulence_intensity = (
            weather_df["turbulence_intensity"].values.mean()
            if "turbulence_intensity" in weather_df.columns.get_level_values(0)
            else None
        )
        roughness_length = (
            weather_df["roughness_length"].values.mean()
            if "roughness_length" in weather_df.columns.get_level_values(0)
            else None
        )
        # Assign power curve
        if (
            self.wake_losses_model == "wind_farm_efficiency"
            or self.wake_losses_model is None
        ):
            wake_losses_model_to_power_curve = self.wake_losses_model
            if self.wake_losses_model is None:
                logging.debug("Wake losses in wind farms are not considered.")
            else:
                logging.debug(
                    "Wake losses considered with {}.".format(
                        self.wake_losses_model
                    )
                )
        else:
            logging.debug(
                "Wake losses considered by {} wind ".format(
                    self.wake_losses_model
                )
                + "efficiency curve."
            )
            wake_losses_model_to_power_curve = None
        self.power_plant.assign_power_curve(
            wake_losses_model=wake_losses_model_to_power_curve,
            smoothing=self.smoothing,
            block_width=self.block_width,
            standard_deviation_method=self.standard_deviation_method,
            smoothing_order=self.smoothing_order,
            roughness_length=roughness_length,
            turbulence_intensity=turbulence_intensity,
        )
        # Further logging messages
        if self.smoothing is False:
            logging.debug("Aggregated power curve not smoothed.")
        else:
            logging.debug(
                "Aggregated power curve smoothed by method: "
                + self.standard_deviation_method
            )

        return self

    def run_model(self, weather_df):
        r"""
        Runs the model.

        Parameters
        ----------
        weather_df : :pandas:`pandas.DataFrame<frame>`
            DataFrame with time series for wind speed `wind_speed` in m/s, and
            roughness length `roughness_length` in m, as well as optionally
            temperature `temperature` in K, pressure `pressure` in Pa,
            density `density` in kg/m³ and turbulence intensity
            `turbulence_intensity` depending on `power_output_model`,
            `density_model` and `standard_deviation_model` chosen.
            The columns of the DataFrame are a MultiIndex where the first level
            contains the variable name (e.g. wind_speed) and the second level
            contains the height at which it applies (e.g. 10, if it was
            measured at a height of 10 m). See below for an example on how to
            create the weather_df DataFrame.

        Returns
        -------
        self

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

        self.assign_power_curve(weather_df)
        self.power_plant.mean_hub_height()
        wind_speed_hub = self.wind_speed_hub(weather_df)
        density_hub = (
            None
            if (
                self.power_output_model == "power_curve"
                and self.density_correction is False
            )
            else self.density_hub(weather_df)
        )
        if (
            self.wake_losses_model != "wind_farm_efficiency"
            and self.wake_losses_model is not None
        ):
            # Reduce wind speed with wind efficiency curve
            wind_speed_hub = wake_losses.reduce_wind_speed(
                wind_speed_hub,
                wind_efficiency_curve_name=self.wake_losses_model,
            )
        self.power_output = self.calculate_power_output(
            wind_speed_hub, density_hub
        )
        return self
