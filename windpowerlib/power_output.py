# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:22:35 2017

@author: RL-INSTITUT\sabine.haas
"""

"""
The ``power_output`` module contains methods
to calculate the power output of a wind turbine.
"""
import numpy as np


def tpo_through_cp(weather, data_height, v_wind, rho_hub, d_rotor, cp_series):
    r"""
    Calculates the power output in W of one wind turbine using cp values.
    This function is carried out when the parameter 'tp_output_model' of an
    object of the class SimpleWindTurbine is 'cp_values'.

    Parameters
    ----------
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : dictionary
        Containing the heights of the weather measurements or weather
        model in meters with the keys of the data parameter
    v_wind : pandas.Series
        wind speed [m/s] at hub height as time series
    rho_hub : pandas.Series
        density of air in kg/m³ at hub height
    d_rotor : float
        diameter of rotor in m
    cp_series : numpy.array
        cp values

    Returns
    -------
    pandas.Series or numpy.array
        Electrical power of the wind turbine

    Notes
    -----
    The following equation is used for the power output [21],[26]_:
    .. math:: P_{wpp}=\frac{1}{8}\cdot\rho_{air,hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        v: wind speed [m/s], d: diameter [m], :math:`\rho`: density [kg/m³]

    References
    ----------
    .. [21] Gasch R., Twele J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, pages 35ff, 208
    .. [26] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 542
    """
    return (rho_hub / 2) * (((d_rotor / 2) ** 2)
                            * np.pi) * np.power(v_wind, 3) * cp_series


def tpo_through_P(p_values, v_wind):
    r"""
    Interpolates the P value as a function of the wind velocity between
    data obtained from the power curve of the specified wind turbine type.
    This fuction is carried out when the parameter 'tp_output_model' of an
    object of the class SimpleWindTurbine is 'p_values'.

    Parameters
    ----------
    p_values : pandas.DataFrame
        P values
    v_wind : pandas.Series
        wind speed [m/s] at hub height as time series

    Returns
    -------
    numpy.array
        Electrical power of the wind turbine

    Note
    ----
    See also cp_series in the module modelchain
    """
    v_max = p_values.index.max()
    v_wind[v_wind > v_max] = v_max
    return np.interp(v_wind, p_values.index, p_values.P)


def Interpolate_P_curve(v_wind, rho_hub, p_values):
    r"""
    Interpolates density corrected power curve.

    Parameters
    ----------
    v_wind : pandas.Series
        wind speed [m/s] at hub height as time series
    rho_hub : pandas.Series
        density of air in kg/m³ at hub height
    p_values : pandas.DataFrame
        P values

    Returns
    -------
    numpy.array
        Electrical power of the wind turbine

    Notes
    -----
    The following equation is used for the wind speed at site
    [28], [29], [30]_:
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

    :math:`v_{std}` is the standard wind speed in power curve

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
    return [(np.interp(v_wind[i], p_values.index *
            (1.225 / rho_hub[i])**(np.interp(p_values.index, [7.5, 12.5],
                                             [1/3, 2/3])),
            p_values.P, left=0, right=0)) for i in range(len(v_wind))]
