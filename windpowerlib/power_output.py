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

    Parameters
    ----------
    weather : feedinlib.weather.FeedinWeather object
        Instance of the feedinlib weather object (see class
        :py:class:`FeedinWeather<feedinlib.weather.FeedinWeather>` for more
        details)
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
        cp values, wind converter type, installed capacity


    # TODO Move the following parameters to a better place :-)

    Returns
    -------
    pandas.Series
        Electrical power of the wind turbine

    Notes
    -----
    The following equation is used for the power output :math:`P_{wpp}`
    [21],[26]_:

    .. math:: P_{wpp}=\frac{1}{8}\cdot\rho_{air,hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        v: wind speed [m/s], d: diameter [m], :math:`\rho`: density [kg/m³]

    ToDo: Check the equation and add references.

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
    See also cp_series in modelchain
    """
    v_max = p_values.index.max()
    v_wind[v_wind > v_max] = v_max
    return np.interp(v_wind, p_values.index, p_values.P)
