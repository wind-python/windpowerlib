"""
The ``power_output`` module contains functions to calculate the power output
of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
import pandas as pd
from windpowerlib import tools
from matplotlib import pyplot as plt
import os


def power_coefficient_curve(wind_speed, power_coefficient_curve_wind_speeds,
                            power_coefficient_curve_values, rotor_diameter,
                            density, density_correction=False):
    r"""
    Calculates the turbine power output using a power coefficient curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is
    'power_coefficient_curve'. If the parameter `density_correction` is True
    the density corrected power curve (See
    :py:func:`~.power_curve_density_correction`) is used.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed at hub height in m/s.
    power_coefficient_curve_wind_speeds : pandas.Series or numpy.array
        Wind speeds in m/s for which the power coefficients are provided in
        `power_coefficient_curve_values`.
    power_coefficient_curve_values : pandas.Series or numpy.array
        Power coefficients corresponding to wind speeds in
        `power_coefficient_curve_wind_speeds`.
    rotor_diameter : float
        Rotor diameter in m.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³.
    density_correction : boolean
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. Default: False.

    Returns
    -------
    pandas.Series or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used if the parameter `density_corr` is False
    [1]_, [2]_:

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
    if density_correction is False:
        power_coefficient_time_series = np.interp(
            wind_speed, power_coefficient_curve_wind_speeds,
            power_coefficient_curve_values, left=0, right=0)
        power_output = (1 / 8 * density * rotor_diameter ** 2 * np.pi *
                        np.power(wind_speed, 3) *
                        power_coefficient_time_series)
        # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
        if isinstance(wind_speed, pd.Series):
            power_output = pd.Series(data=power_output, index=wind_speed.index,
                                     name='feedin_wind_turbine')
        else:
            power_output = np.array(power_output)
    elif density_correction is True:
        power_curve_values = (1 / 8 * 1.225 * rotor_diameter ** 2 * np.pi *
                              np.power(power_coefficient_curve_wind_speeds,
                                       3) *
                              power_coefficient_curve_values)
        power_output = power_curve_density_correction(
            wind_speed, power_coefficient_curve_wind_speeds,
            power_curve_values, density)
    else:
        raise TypeError("'{0}' is an invalid type. ".format(type(
                        density_correction)) + "`density_correction` must " +
                        "be Boolean (True or False).")
    return power_output


def power_curve(wind_speed, power_curve_wind_speeds, power_curve_values,
                density=None, density_correction=False):
    r"""
    Calculates the turbine power output using a power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'power_curve'. If
    the parameter `density_correction` is True the density corrected power
    curve (See :py:func:`~.power_curve_density_correction`) is used.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed at hub height in m/s.
    power_curve_wind_speeds : pandas.Series or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³. This parameter is needed
        if `density_correction` is True. Default: None.
    density_correction : boolean
        If the parameter is True the density corrected power curve is used for
        the calculation of the turbine power output. In this case `density`
        cannot be None. Default: False.

    Returns
    -------
    pandas.Series or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -------
    It is assumed that the power output for wind speeds above the maximum
    and below the minimum wind speed given in the power curve is zero.

    """
    if density_correction is False:
        power_output = np.interp(wind_speed, power_curve_wind_speeds,
                                 power_curve_values, left=0, right=0)
        # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
        if isinstance(wind_speed, pd.Series):
            power_output = pd.Series(data=power_output, index=wind_speed.index,
                                     name='feedin_wind_turbine')
        else:
            power_output = np.array(power_output)
    elif density_correction is True:
        power_output = power_curve_density_correction(
            wind_speed, power_curve_wind_speeds, power_curve_values, density)
    else:
        raise TypeError("'{0}' is an invalid type. ".format(type(
                        density_correction)) + "`density_correction` must " +
                        "be Boolean (True or False).")
    return power_output


def power_curve_density_correction(wind_speed, power_curve_wind_speeds,
                                   power_curve_values, density):
    # possible TODO: add density correction for stall controlled wind turbines
    r"""
    Calculates the turbine power output using a density corrected power curve.

    This function is carried out when the parameter `density_correction` of an
    instance of the :class:`~.modelchain.ModelChain` class is True.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed at hub height in m/s.
    power_curve_wind_speeds : pandas.Series or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³.

    Returns
    -------
    pandas.Series or numpy.array
        Electrical power output of the wind turbine in W.
        Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used for the wind speed at site
    [1]_, [2]_, [3]_:

    .. math:: v_{site}=v_{std}\cdot\left(\frac{\rho_0}
                       {\rho_{site}}\right)^{p(v)}

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
        raise TypeError("`density` is None. For the calculation with a " +
                        "density corrected power curve density at hub " +
                        "height is needed.")
    power_output = [(np.interp(
        wind_speed[i], power_curve_wind_speeds * (1.225 / density[i]) ** (
            np.interp(power_curve_wind_speeds, [7.5, 12.5], [1/3, 2/3])),
        power_curve_values, left=0, right=0)) for i in range(len(wind_speed))]

    # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
    if isinstance(wind_speed, pd.Series):
        power_output = pd.Series(data=power_output, index=wind_speed.index,
                                 name='feedin_wind_turbine')
    else:
        power_output = np.array(power_output)
    return power_output


def smooth_power_curve(power_curve_wind_speeds, power_curve_values,
                       block_width=0.5,
                       standard_deviation_method='turbulence_intensity',
                       mean_gauss=0, **kwargs):
    r"""
    Smoothes the input power curve values by using a gaussian distribution.

    Parameters
    ----------
    power_curve_wind_speeds : pandas.Series
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    block_width : Float
        Width of the moving block. Default: 0.5.
    standard_deviation_method : String
        Method for calculating the standard deviation for the gaussian
        distribution. Options: 'turbulence_intensity', 'Norgaard', 'Staffell'.
        Default: 'turbulence_intensity'.

    Other Parameters
    ----------------
    turbulence intensity : Float, optional
        Turbulence intensity at hub height of the wind turbine the power curve
        is smoothed for.

    Returns
    -------
    smoothed_power_curve_df : pd.DataFrame
        Smoothed power curve. DataFrame has 'wind_speed' and
        'values' columns with wind speeds in m/s and the corresponding power
        curve value in W.

    Notes
    -----
    The following equation is used [1]_:
        # TODO: add equations

    References
    ----------
    .. [1] Knorr p. 106
    # TODO: add references
    """
    # Specify normalized standard deviation
    if standard_deviation_method == 'turbulence_intensity':
        if 'turbulence_intensity' in kwargs:
            normalized_standard_deviation = kwargs['turbulence_intensity']
        else:
            raise ValueError("Turbulence intensity must be defined for " +
                             "using 'turbulence_intensity' as " +
                             "`standard_deviation_method`")
    elif standard_deviation_method == 'Norgaard':
        pass # TODO add
    elif standard_deviation_method == 'Staffell':
        normalized_standard_deviation = 0.2
    # Initialize list for power curve values
    smoothed_power_curve_values = []
    # Step of power curve wind speeds
    step = power_curve_wind_speeds.iloc[-5] - power_curve_wind_speeds.iloc[-6]
    # Append wind speeds to `power_curve_wind_speeds` until 40 m/s
    while (power_curve_wind_speeds.values[-1] < 40.0):
        power_curve_wind_speeds = power_curve_wind_speeds.append(
            pd.Series(power_curve_wind_speeds.iloc[-1] + step,
                      index=[power_curve_wind_speeds.index[-1] + 1]))
        power_curve_values = power_curve_values.append(
            pd.Series(0.0, index=[power_curve_values.index[-1] + 1]))
    for power_curve_wind_speed in power_curve_wind_speeds:
        # Create array of wind speeds for the moving block
        wind_speeds_block = (
            np.arange(-15.0, 15.0 + block_width, block_width) +
            power_curve_wind_speed)
        # Get standard deviation for gaussian filter
        standard_deviation = (
            (power_curve_wind_speed * normalized_standard_deviation + 0.6)
            if standard_deviation_method is 'Staffell'
            else power_curve_wind_speed * normalized_standard_deviation)
        # Get the smoothed value of the power output
        smoothed_value = sum(
            block_width * np.interp(wind_speed, power_curve_wind_speeds,
                                    power_curve_values, left=0, right=0) *
            tools.gaussian_distribution(
                power_curve_wind_speed - wind_speed,
                standard_deviation, mean_gauss)
            for wind_speed in wind_speeds_block)
        # Add value to list - add 0 if `smoothed_value` is nan. This occurs
        # because the gaussian distribution is not defined for 0.
        smoothed_power_curve_values.append(0 if np.isnan(smoothed_value)
                                           else smoothed_value)
    # Create smoothed power curve DataFrame
    smoothed_power_curve_df = pd.DataFrame(
        data=[list(power_curve_wind_speeds.values),
              smoothed_power_curve_values]).transpose()
    # Rename columns of DataFrame
    smoothed_power_curve_df.columns = ['wind_speed', 'values']
#    # Plot power curves
#    fig = plt.figure()
#    plt.plot(power_curve_wind_speeds.values, power_curve_values.values)
#    plt.plot(power_curve_wind_speeds.values, smoothed_power_curve_values)
#    fig.savefig(os.path.abspath(os.path.join(
#        os.path.dirname(__file__), '../Plots/power_curves',
#        '{0}_{1}_{2}.png'.format(kwargs['object_name'],
#                                 standard_deviation_method, block_width))))
#    plt.close()
    return smoothed_power_curve_df


def summarized_power_curve(wind_turbine_fleet, smoothing=True,
                           density_correction=False, wake_losses=False,
                           **kwargs):
    r"""
    TODO: add to docstring

    Parameters
    ----------
    wind_turbine_fleet : List of Dictionaries
        Dictionaries with the keys 'wind_turbine' (contains
        :class:`~.wind_turbine.WindTurbine` object) and 'number_of_turbines'
        (contains number of turbine type in 'wind_turbine' key).
    smoothing : Boolean
        If True the power curves will be smoothed before the summation.
        Default: True.
    density_correction : Boolean
        If True a density correction will be applied to the power curves
        before the summation. Default: False.
    wake_losses : Boolean
        If True wake losses within the farm are taken into consideration.
        Default: False.

    Other Parameters
    ----------------
    block_width : Float, optional
        Width of the moving block.
        Default in :py:func:`~.smooth_power_curve`: 0.5.
    standard_deviation_method : String, optional
        Method for calculating the standard deviation for the gaussian
        distribution. Options: 'turbulence_intensity', 'Norgaard', 'Staffell'.
        Default in :py:func:`~.smooth_power_curve`:  'turbulence_intensity'.
    turbulence_intensity : Float, optional
        Turbulence intensity at hub height of the wind turbine the power curve
        is smoothed for. If this parameter is not given the turbulence
        intensity is calculated via the `roughness_length`.
    roughness_length : Float, optional
        Roughness length. Only needed if `turbulence_intensity` is not given
        and `standard_deviation_method` is 'turbulence_intensity' or not given.

    Returns
    -------
    summarized_power_curve_df : pd.DataFrame
        Summarized power curve. DataFrame has 'wind_speed' and
        'values' columns with wind speeds in m/s and the corresponding power
        curve value in W.

    """
    df = pd.DataFrame()
    for turbine_type_dict in wind_turbine_fleet:
        if not smoothing and not density_correction:
            power_curve = turbine_type_dict['wind_turbine'].power_curve
        if smoothing:
            if ('standard_deviation_method' not in kwargs or
                    kwargs['standard_deviation_method'] ==
                    'turbulence_intensity'):
                if 'turbulence_intensity' not in kwargs:
                    if 'roughness_length' in kwargs:
                        turbulence_intensity = tools.estimate_turbulence_intensity(
                            turbine_type_dict['wind_turbine'].hub_height,
                            kwargs['roughness_length'])
                        kwargs['turbulence_intensity'] = turbulence_intensity
                    else:
                        raise ValueError("`roughness_length` must be " +
                                         "defined for using " +
                                         "'turbulence_intensity' as " +
                                         "`standard_deviation_method`")
            power_curve = smooth_power_curve(
                turbine_type_dict['wind_turbine'].power_curve['wind_speed'],
                turbine_type_dict['wind_turbine'].power_curve['values'],
                **kwargs)
        if density_correction:
            pass  # TODO: add
        # Add sum of power curves to DataFrame df
        power_curve.columns = ['wind_speed',
                               turbine_type_dict['wind_turbine'].object_name]
        df = pd.concat([df, pd.DataFrame(power_curve.set_index(
            ['wind_speed']) * turbine_type_dict['number_of_turbines'])],
                       axis=1)
    # Sum up all power curves
    summarized_power_curve = sum(df[item].interpolate(method='index')
                                 for item in list(df))
    # Create summarized power curve DataFrame
    summarized_power_curve_df = pd.DataFrame(
        data=[list(summarized_power_curve.index),
              list(summarized_power_curve.values)]).transpose()
    # Rename columns of DataFrame
    summarized_power_curve_df.columns = ['wind_speed', 'values']
    return summarized_power_curve_df
