"""
The ``power_output`` module contains functions to calculate the power output
of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
import pandas as pd


def power_coefficient_curve(wind_speed, cp_values,
                            rotor_diameter, density, density_corr=False):
    r"""
    Calculates the turbine power output using a power coefficient curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'cp_values'. If
    the parameter `density_corr` is True the density corrected power curve
    (:py:func:`~._p_curve_density_corr`) is used.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed at hub height in m/s.
    cp_values : pandas.Series
        Power coefficient curve of the wind turbine.
        Indices are the wind speeds of the power coefficient curve in m/s.
    rotor_diameter : float
        Rotor diameter in m.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³.
    density_corr : boolean
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
    if density_corr is False:
        cp_time_series = np.interp(wind_speed, cp_values.index, cp_values,
                                   left=0, right=0)
        power_output = (1 / 8 * density * rotor_diameter ** 2 * np.pi
                        * np.power(wind_speed, 3) * cp_time_series)
    elif density_corr is True:
        p_values = (1 / 8 * 1.225 * rotor_diameter ** 2 * np.pi *
                    np.power(cp_values.index, 3) * cp_values)
        p_values = pd.Series(np.array(p_values), index=cp_values.index)
        power_output = _p_curve_density_corr(wind_speed, density, p_values)
    else:
        raise TypeError("'{0}' is an invalid type.".format(type(
                        density_corr)) + "`density_corr` must be Boolean " +
                        "(True or False).")

    # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
    if isinstance(wind_speed, pd.Series):
        power_output = pd.Series(data=power_output, index=wind_speed.index,
                                 name='feedin_wind_turbine')
    else:
        power_output = np.array(power_output)
    return power_output


def power_curve(wind_speed, p_values, density=None, density_corr=False):
    r"""
    Calculates the turbine power output using a power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'p_values'. If
    the parameter `density_corr` is True the density corrected power curve
    (:py:func:`~._p_curve_density_corr`) is used.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed at hub height in m/s.
    p_values : pandas.Series
        Power curve of the wind turbine.
        Indices are the wind speeds of the power curve in m/s.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³. This parameter is needed
        if `density_corr` is True. Default: None.
    density_corr : boolean
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
    if density_corr is False:
        power_output = np.interp(wind_speed, p_values.index, p_values,
                                 left=0, right=0)
    elif density_corr is True:
        power_output = _p_curve_density_corr(wind_speed, p_values, density)
    else:
        raise TypeError("'{0}' is an invalid type.".format(type(
                        density_corr)) + "`density_corr` must be Boolean " +
                        "(True or False).")
    # Power_output as pd.Series if wind_speed is pd.Series (else: np.array)
    if isinstance(wind_speed, pd.Series):
        power_output = pd.Series(data=power_output, index=wind_speed.index,
                                 name='feedin_wind_turbine')
    else:
        power_output = np.array(power_output)
    return power_output


def _p_curve_density_corr(wind_speed, p_values, density):
    r"""
    Calculates the turbine power output using a density corrected power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'p_values' and
    the parameter `density_corr` is True.

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed time series at hub height in m/s.
    p_values : pandas.Series
        Power curve of the wind turbine.
        Indices are the wind speeds of the power curve in m/s.
    density : pandas.Series or numpy.array
        Density of air at hub height in kg/m³.

    Returns
    -------
    list
        Electrical power output of the wind turbine in W.

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
                        "density corrected power curve density at hub height" +
                        "is needed.")
    return[(np.interp(wind_speed[i],
                      p_values.index * (1.225 / density[i])**(
                          np.interp(p_values.index, [7.5, 12.5], [1/3, 2/3])),
                      p_values, left=0, right=0))
           for i in range(len(wind_speed))]
