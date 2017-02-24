"""
The ``power_output`` module contains methods to calculate the power output
of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
import pandas as pd


def cp_curve(v_wind, rho_hub, d_rotor, cp_values):
    r"""
    Calculates the power output of one wind turbine using a cp curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class
    is 'cp_values' and the parameter `density_corr` is False.

    Parameters
    ----------
    v_wind : pandas.Series or array
        Wind speed time series at hub height in m/s.
    rho_hub : pandas.Series or array
        Density of air at hub height in kg/m³.
    d_rotor : float
        Diameter of rotor in m.
    cp_values : pandas.DataFrame
        Curve of the power coefficient of the wind turbine.
        The indices are the corresponding wind speeds of the power coefficient
        curve, the power coefficient values containing column is called 'cp'.

    Returns
    -------
    pandas.Series
        Electrical power output of the wind turbine in W.

    Notes
    -----
    The following equation is used for the power output [21]_, [26]_:

    .. math:: p _{wpp}=\frac{1}{8}\cdot\rho_{hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        v: wind speed [m/s], d: diameter [m], :math:`\rho`: density [kg/m³]

    References
    ----------
    .. [21] Gasch, R., Twele, J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, pages 35ff, 208
    .. [26] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 542

    """
    # cp time series
    v_max = cp_values.index.max()
    v_wind[v_wind > v_max] = v_max
    cp_series = np.interp(v_wind, cp_values.index, cp_values.cp)
    return (1 / 8 * rho_hub * d_rotor ** 2 * np.pi * np.power(v_wind, 3) *
            cp_series)


def p_curve(p_values, v_wind):
    r"""
    Converts power curve to power output of wind turbine.

    Interpolates the values of the power curve as a function of the wind speed
    between data obtained from the power curve of the specified wind turbine
    type.
    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class
    is 'p_values' and the parameter `density_corr` is False.

    Parameters
    ----------
    p_values : pandas.DataFrame
        Power curve of the wind turbine
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.
    v_wind : pandas.Series or array
        Wind speed time series at hub height in m/s.

    Returns
    -------
    power_output : pandas.Series
        Electrical power of the wind turbine.

    Note
    ----
    See also cp_series() in the module ``modelchain``.

    """
    v_max = p_values.index.max()
    v_wind[v_wind > v_max] = v_max
    power_output = np.interp(v_wind, p_values.index, p_values.P)
    # Set index for time series
    try:
        series_index = v_wind.index
    except AttributeError:
        series_index = range(1, len(power_output)+1)
    power_output = pd.Series(data=power_output, index=series_index,
                             name='feedin_wind_pp')
    power_output.index.names = ['']
    return power_output


def p_curve_density_corr(v_wind, rho_hub, p_values):
    r"""
    Interpolates density corrected power curve.

    This function is carried out when the parameter `density_corr` of an
    object of the class WindTurbine is True.

    Parameters
    ----------
    v_wind : pandas.Series or array
        Wind speed time series at hub height in m/s.
    rho_hub : pandas.Series or array
        Density of air at hub height in kg/m³.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.

    Returns
    -------
    power_output : pandas.Series
        Electrical power of the wind turbine.

    Notes
    -----
    The following equation is used for the wind speed at site
    [28]_, [29]_, [30]_:

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
    (:math:`v_{std}`, :math:`P_{std}`).
    :math:`v_{site}` is the density corrected wind speed for the power curve
    (:math:`v_{site}`, :math:`P_{std}`).

    References
    ----------
    .. [28] Svenningsen, L.: "Power Curve Air Density Correction And Other
            Power Curve Options in WindPRO". 1st edition, Aalborg,
            EMD International A/S , 2010, p. 4
    .. [29] Svenningsen, L.: "Proposal of an Improved Power Curve Correction".
            EMD International A/S , 2010
    .. [30] Biank, M.: "Methodology, Implementation and Validation of a
            Variable Scale Simulation Model for Windpower based on the
            Georeferenced Installation Register of Germany". Master's Thesis
            at RLI, 2014, p. 13

    """
    # Calulation of v_site and interpolation of density corrected power curve
    # for every wind speed in the time series `v_wind`.
    for i in range(len(v_wind)):
        v_site = (p_values.index * (1.225 / rho_hub[i]) **
                 (np.interp(p_values.index, [7.5, 12.5], [1/3, 2/3])))
        power_output = np.interp(v_wind[i], v_site, p_values.P)

    # Set index for time series
    try:
        series_index = v_wind.index
    except AttributeError:
        series_index = range(1, len(power_output)+1)
    power_output = pd.Series(data=power_output, index=series_index,
                             name='feedin_wind_pp')
    power_output.index.names = ['']
    return power_output
