"""
The ``power_output`` module contains functions to calculate the power output
of a wind turbine.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import pandas as pd


def power_coefficient_curve(
    wind_speed,
    power_coefficient_curve_wind_speeds,
    power_coefficient_curve_values,
    rotor_diameter,
    density,
):
    r"""
    Calculates the turbine power output using a power coefficient curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is
    'power_coefficient_curve'.

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height in m/s.
    power_coefficient_curve_wind_speeds : :pandas:`pandas.Series<series>` or numpy.array
        Wind speeds in m/s for which the power coefficients are provided in
        `power_coefficient_curve_values`.
    power_coefficient_curve_values : :pandas:`pandas.Series<series>` or numpy.array
        Power coefficients corresponding to wind speeds in
        `power_coefficient_curve_wind_speeds`.
    rotor_diameter : float
        Rotor diameter in m.
    density : :pandas:`pandas.Series<series>` or numpy.array
        Density of air at hub height in kg/m³.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used [1]_ [2]_:

    .. math:: P=\frac{1}{8}\cdot\rho_{hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        P: power [W], :math:`\rho`: density [kg/m³], d: diameter [m],
        v: wind speed [m/s], cp: power coefficient

    It is assumed that the power output for wind speeds above the maximum
    and below the minimum wind speed given in the power coefficient curve is
    zero.

    References
    ----------
    .. [1] Gasch, R., Twele, J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, pages 35ff, 208
    .. [2] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 542

    """
    power_coefficient_time_series = np.interp(
        wind_speed,
        power_coefficient_curve_wind_speeds,
        power_coefficient_curve_values,
        left=0,
        right=0,
    )
    power_output = (
        1
        / 8
        * density
        * rotor_diameter ** 2
        * np.pi
        * np.power(wind_speed, 3)
        * power_coefficient_time_series
    )
    # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
    if isinstance(wind_speed, pd.Series):
        power_output = pd.Series(
            data=power_output,
            index=wind_speed.index,
            name="feedin_power_plant",
        )
    else:
        power_output = np.array(power_output)
    return power_output


def power_curve(
    wind_speed,
    power_curve_wind_speeds,
    power_curve_values,
    density=None,
    density_correction=False,
):
    r"""
    Calculates the turbine power output using a power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'power_curve'. If
    the parameter `density_correction` is True the density corrected power
    curve (see :py:func:`~.power_curve_density_correction`) is used.

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height in m/s.
    power_curve_wind_speeds : :pandas:`pandas.Series<series>` or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    density : :pandas:`pandas.Series<series>` or numpy.array
        Density of air at hub height in kg/m³. This parameter is needed
        if `density_correction` is True. Default: None.
    density_correction : bool
        If the parameter is True the density corrected power curve (see
        :py:func:`~.power_curve_density_correction`) is used for the
        calculation of the turbine power output. In this case `density`
        cannot be None. Default: False.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -------
    It is assumed that the power output for wind speeds above the maximum
    and below the minimum wind speed given in the power curve is zero.

    """
    if density_correction is False:
        power_output = np.interp(
            wind_speed,
            power_curve_wind_speeds,
            power_curve_values,
            left=0,
            right=0,
        )
        # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
        if isinstance(wind_speed, pd.Series):
            power_output = pd.Series(
                data=power_output,
                index=wind_speed.index,
                name="feedin_power_plant",
            )
        else:
            power_output = np.array(power_output)
    elif density_correction is True:
        power_output = power_curve_density_correction(
            wind_speed, power_curve_wind_speeds, power_curve_values, density
        )
    else:
        raise TypeError(
            "'{0}' is an invalid type. ".format(type(density_correction))
            + "`density_correction` must "
            + "be Boolean (True or False)."
        )
    return power_output


def power_curve_density_correction(
    wind_speed, power_curve_wind_speeds, power_curve_values, density
):
    r"""
    Calculates the turbine power output using a density corrected power curve.
    This function is carried out when the parameter `density_correction` of an
    instance of the :class:`~.modelchain.ModelChain` class is True.

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height in m/s.
    power_curve_wind_speeds : :pandas:`pandas.Series<series>` or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : :pandas:`pandas.Series<series>` or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    density : :pandas:`pandas.Series<series>` or numpy.array
        Density of air at hub height in kg/m³.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used for the site specific power curve wind
    speeds [1]_ [2]_ [3]_:

    .. math:: v_{site}=v_{std}\cdot\left(\frac{\rho_0}{\rho_{site}}\right)^{p(v)}

    with:
        .. math:: p=\begin{cases}
                      \frac{1}{3} & v_{std} \leq 7.5\text{ m/s}\\
                      \frac{1}{15}\cdot v_{std}-\frac{1}{6} & 7.5
                      \text{ m/s}<v_{std}<12.5\text{ m/s}\\
                      \frac{2}{3} & \geq 12.5 \text{ m/s}
                    \end{cases},

        v: wind speed [m/s], :math:`\rho`: density [kg/m³]

    :math:`v_{std}` is the standard wind speed in the power curve
    (:math:`v_{std}`, :math:`P_{std}`),
    :math:`v_{site}` is the density corrected wind speed for the power curve
    (:math:`v_{site}`, :math:`P_{std}`),
    :math:`\rho_0` is the ambient density (1.225 kg/m³)
    and :math:`\rho_{site}` the density at site conditions (and hub height).
    It is assumed that the power output for wind speeds above the maximum
    and below the minimum wind speed given in the power curve is zero.

    References
    ----------
    .. [1] Svenningsen, L.: "Power Curve Air Density Correction And Other
           Power Curve Options in WindPRO". 1st edition, Aalborg,
           EMD International A/S , 2010, p. 4
    .. [2] Svenningsen, L.: "Proposal of an Improved Power Curve Correction".
           EMD International A/S , 2010
    .. [3] Biank, M.: "Methodology, Implementation and Validation of a
           Variable Scale Simulation Model for Windpower based on the
           Georeferenced Installation Register of Germany". Master's Thesis
           at Reiner Lemoine Institute, 2014, p. 13

    """
    if density is None:
        raise TypeError(
            "`density` is None. For the calculation with a "
            + "density corrected power curve density at hub "
            + "height is needed."
        )

    # Convert pd.Series to a numpy array to speed up the interpolation below.
    if isinstance(wind_speed, pd.Series):
        # save the indexes for later conversion to pd.Series
        wind_speed_indexes = wind_speed.index
        # change the wind speed Series to numpy array
        wind_speed = wind_speed.values
        # Set the panda series flag True
        panda_series = True
    else:
        panda_series = False

    power_output = _get_power_output(
        wind_speed,
        np.array(power_curve_wind_speeds),
        np.array(density),
        np.array(power_curve_values),
    )

    # Convert results to the data type of the input data
    if panda_series:
        power_output = pd.Series(
            data=power_output,
            index=wind_speed_indexes,  # Use previously saved wind speed index
            name="feedin_power_plant",
        )

    return power_output


def _get_power_output(
    wind_speed, power_curve_wind_speeds, density, power_curve_values
):
    """Get the power output at each timestep using only numpy to speed up performance

    Parameters
    ----------
    wind_speed : :numpy:`numpy.ndarray`
        Wind speed at hub height in m/s.
    power_curve_wind_speeds : :numpy:`numpy.ndarray`
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    density : :numpy:`numpy.ndarray`
        Density of air at hub height in kg/m³.
    power_curve_values : :numpy:`numpy.ndarray`
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.

    Returns
    -------
    :numpy:`numpy.array`
        Electrical power output of the wind turbine in W.

    """
    # Calculate the power curves for each timestep using vectors
    # NOTE: power_curves_per_ts.shape = [len(wind_speed), len(density)]
    power_curves_per_ts = (
        (1.225 / density).reshape(-1, 1)
        ** np.interp(power_curve_wind_speeds, [7.5, 12.5], [1 / 3, 2 / 3])
    ) * power_curve_wind_speeds

    # Create the interpolation function
    def interp_func(w_speed, p_curves):
        return np.interp(
            w_speed, p_curves, power_curve_values, left=0, right=0
        )

    # Calculate the power output by mapping the arrays to the interp function
    power_output = np.array(
        list(map(interp_func, wind_speed, power_curves_per_ts))
    )

    return power_output
