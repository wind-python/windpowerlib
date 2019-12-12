"""
The ``power_curves`` module contains functions for applying alterations like
power curve smoothing or reducing power values by an efficiency to the power
curve of a wind turbine, wind farm or wind turbine cluster.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import pandas as pd
from windpowerlib import tools


def smooth_power_curve(power_curve_wind_speeds, power_curve_values,
                       block_width=0.5, wind_speed_range=15.0,
                       standard_deviation_method='turbulence_intensity',
                       mean_gauss=0, **kwargs):
    r"""
    Smoothes a power curve by using a Gauss distribution.

    The smoothing serves for taking the distribution of wind speeds over space
    into account.

    Parameters
    ----------
    power_curve_wind_speeds : :pandas:`pandas.Series<series>` or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : :pandas:`pandas.Series<series>` or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    block_width : float
        Width between the wind speeds in the sum of equation :eq:`power`.
        Default: 0.5.
    wind_speed_range : float
        The sum in the equation below is taken for this wind speed range below
        and above the power curve wind speed. Default: 15.0.
    standard_deviation_method : str
        Method for calculating the standard deviation for the Gauss
        distribution. Options: 'turbulence_intensity', 'Staffell_Pfenninger'.
        Default: 'turbulence_intensity'.
    mean_gauss : float
        Mean of the Gauss distribution in
        :py:func:`~.tools.gauss_distribution`. Default: 0.

    Other Parameters
    ----------------
    turbulence intensity : float, optional
        Turbulence intensity at hub height of the wind turbine, wind farm or
        wind turbine cluster the power curve is smoothed for.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Smoothed power curve. DataFrame has 'wind_speed' and 'value' columns
        with wind speeds in m/s and the corresponding power curve value in W.

    Notes
    -----
    The following equation is used to calculated the power curves values of the
    smoothed power curve [1]_:

    .. math:: P_{smoothed}(v_{std})=\sum\limits_{v_i} \Delta v_i \cdot P(v_i)
        \cdot \frac{1}{\sigma \sqrt{2 \pi}}
        \exp \left[-\frac{(v_{std} - v_i -\mu)^2}{2 \sigma^2} \right]
       :label: power

    with:
        P: power [W], v: wind speed [m/s],
        :math:`\sigma`: standard deviation (Gauss), :math:`\mu`: mean (Gauss)

        :math:`P_{smoothed}` is the smoothed power curve value,
        :math:`v_{std}` is the standard wind speed in the power curve,
        :math:`\Delta v_i` is the interval length between
        :math:`v_\text{i}` and :math:`v_\text{i+1}`

    Power curve smoothing is applied to take account of the spatial
    distribution of wind speed. This way of smoothing power curves is also used
    in [2]_ and [3]_.

    The standard deviation :math:`\sigma` of the above equation can be
    calculated by the following methods.

    'turbulence_intensity' [2]_:

    .. math:: \sigma=v_\text{std} \cdot \sigma_\text{n}=v_\text{std}
        \cdot TI

    with:
        TI: turbulence intensity

    'Staffell_Pfenninger' [4]_:

    .. math:: \sigma=0.6 \cdot 0.2 \cdot v_\text{std}

    References
    ----------
    .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 106
    .. [2]  Nørgaard, P. and Holttinen, H.: "A Multi-Turbine and Power Curve
             Approach". Nordic Wind Power Conference, 1.–2.3.2004, 2000, p. 5
    .. [3]  Kohler, S. and Agricola, A.-Cl. and Seidl, H.:
             "dena-Netzstudie II. Integration erneuerbarer Energien in die
             deutsche Stromversorgung im Zeitraum 2015 – 2020 mit Ausblick
             2025". Technical report, 2010.
    .. [4]  Staffell, I. and Pfenninger, S.: "Using Bias-Corrected Reanalysis
              to Simulate Current and Future Wind Power Output". 2005, p. 11

    """
    # Specify normalized standard deviation
    if standard_deviation_method == "turbulence_intensity":
        if (
            "turbulence_intensity" in kwargs
            and kwargs["turbulence_intensity"] is not np.nan
        ):
            normalized_standard_deviation = kwargs["turbulence_intensity"]
        else:
            raise ValueError(
                "Turbulence intensity must be defined for "
                + "using 'turbulence_intensity' as "
                + "`standard_deviation_method`"
            )
    elif standard_deviation_method == "Staffell_Pfenninger":
        normalized_standard_deviation = 0.2
    else:
        raise ValueError(
            "{} is no valid `standard_deviation_method`. Valid "
            + "options are 'turbulence_intensity', or "
            + "'Staffell_Pfenninger'".format(standard_deviation_method)
        )
    # Initialize list for power curve values
    smoothed_power_curve_values = []
    # Append wind speeds to `power_curve_wind_speeds`
    maximum_value = power_curve_wind_speeds.iloc[-1] + wind_speed_range
    while power_curve_wind_speeds.values[-1] < maximum_value:
        power_curve_wind_speeds = power_curve_wind_speeds.append(
            pd.Series(
                power_curve_wind_speeds.iloc[-1]
                + (
                    power_curve_wind_speeds.iloc[5]
                    - power_curve_wind_speeds.iloc[4]
                ),
                index=[power_curve_wind_speeds.index[-1] + 1],
            )
        )
        power_curve_values = power_curve_values.append(
            pd.Series(0.0, index=[power_curve_values.index[-1] + 1])
        )
    for power_curve_wind_speed in power_curve_wind_speeds:
        # Create array of wind speeds for the sum
        wind_speeds_block = (
            np.arange(
                -wind_speed_range, wind_speed_range + block_width, block_width
            )
            + power_curve_wind_speed
        )
        # Get standard deviation for Gauss function
        standard_deviation = (
            (power_curve_wind_speed * normalized_standard_deviation + 0.6)
            if standard_deviation_method is "Staffell_Pfenninger"
            else power_curve_wind_speed * normalized_standard_deviation
        )
        # Get the smoothed value of the power output
        if standard_deviation == 0.0:
            # The gaussian distribution is not defined for a standard deviation
            # of zero. Smoothed power curve value is set to zero.
            smoothed_value = 0.0
        else:
            smoothed_value = sum(
                block_width
                * np.interp(
                    wind_speed,
                    power_curve_wind_speeds,
                    power_curve_values,
                    left=0,
                    right=0,
                )
                * tools.gauss_distribution(
                    power_curve_wind_speed - wind_speed,
                    standard_deviation,
                    mean_gauss,
                )
                for wind_speed in wind_speeds_block
            )
        # Add value to list - add zero if `smoothed_value` is nan as Gauss
        # distribution for a standard deviation of zero.
        smoothed_power_curve_values.append(smoothed_value)
    # Create smoothed power curve data frame
    smoothed_power_curve_df = pd.DataFrame(
        data=[
            list(power_curve_wind_speeds.values),
            smoothed_power_curve_values,
        ]
    ).transpose()
    # Rename columns of the data frame
    smoothed_power_curve_df.columns = ["wind_speed", "value"]
    return smoothed_power_curve_df


def wake_losses_to_power_curve(
    power_curve_wind_speeds, power_curve_values, wind_farm_efficiency
):
    r"""
    Reduces the power values of a power curve by an efficiency (curve).

    Parameters
    ----------
    power_curve_wind_speeds : :pandas:`pandas.Series<series>` or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : :pandas:`pandas.Series<series>` or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    wind_farm_efficiency : float or :pandas:`pandas.DataFrame<frame>`
        Efficiency of the wind farm. Either constant (float) or efficiency
        curve (pd.DataFrame) containing 'wind_speed' and 'efficiency' columns
        with wind speeds in m/s and the corresponding dimensionless wind farm
        efficiency (reduction of power). Default: None.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Power curve with power values reduced by a wind farm efficiency.
        DataFrame has 'wind_speed' and 'value' columns with wind speeds in m/s
        and the corresponding power curve value in W.

    """
    # Create power curve DataFrame
    power_curve_df = pd.DataFrame(
        data=[list(power_curve_wind_speeds), list(power_curve_values)]
    ).transpose()
    # Rename columns of DataFrame
    power_curve_df.columns = ["wind_speed", "value"]
    if isinstance(wind_farm_efficiency, float):
        power_curve_df["value"] = power_curve_values * wind_farm_efficiency
    elif isinstance(wind_farm_efficiency, dict) or isinstance(
        wind_farm_efficiency, pd.DataFrame
    ):
        df = pd.concat(
            [
                power_curve_df.set_index("wind_speed"),
                wind_farm_efficiency.set_index("wind_speed"),
            ],
            axis=1,
        )
        # Add column with reduced power (nan values of efficiency are
        # interpolated)
        df["reduced_power"] = df["value"] * df["efficiency"].interpolate(
            method="index"
        )
        reduced_power = df["reduced_power"].dropna()
        power_curve_df = pd.DataFrame(
            [reduced_power.index, reduced_power.values]
        ).transpose()
        power_curve_df.columns = ["wind_speed", "value"]
    else:
        raise TypeError(
            "'wind_farm_efficiency' must be float, dict or pd.DataFrame "
            "but is {}".format(type(wind_farm_efficiency))
        )
    return power_curve_df
