"""The ``wind_speed`` module contains methods to calculate the wind_speed at
hub height of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"

import numpy as np
import sys


def logarithmic_wind_profile(h_hub, weather, data_height, obstacle_height=0):
    r"""
    Calculates the wind speed in m/s at hub height using the logarithmic height
    equation.

    Parameters
    ----------
    h_hub : float
        hub height of wind turbine in m
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).
    obstacle_height : float
        height of obstacles in m in the surroundings of the wind turbine,
        put obstacle_height to zero for wide spread obstacles

    Returns
    -------
    pandas.Series
        wind speed [m/s] at hub height as time series

    Notes
    -----
    The following equation is used for the logarithmic wind profile [27]_:
    .. math:: v_{wind,hub}=v_{wind,data}\cdot
        \frac{\ln\left(\frac{h_{hub}-d}{z_{0}}\right)}{\ln\left(
        \frac{h_{data}-d}{z_{0}}\right)}

    with:
        v: wind speed [m/s], h: height [m], z0: roughness length [m]
        d: includes obstacle height (d = 0.7 * obstacle_height) [m]

    For  d = 0 it results in the following equation [20], [25]_:
    .. math:: v_{wind,hub}=v_{wind,data}\cdot\frac{\ln\left(\frac{h_{hub}}
        {z_{0}}\right)}{\ln\left(\frac{h_{data}}{z_{0}}\right)}

    :math:`h_{data}` is the height in which the wind velocity is measured.
    (height in m, velocity in m/s)

    References
    ----------
    .. [20] Gasch R., Twele J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, page 129
    .. [25] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 515
    .. [27] Quaschning V.: "Regenerative Energiesysteme". München, Hanser
            Verlag, 2011, p. 245
    """
    if 0.7 * obstacle_height > data_height['v_wind']:
        sys.exit('To take an obstacle height of ' + str(obstacle_height) +
                 ' m into consideration wind speed data of a higher height' +
                 ' is needed.')
    return (weather['v_wind'] * np.log(
            (h_hub - 0.7 * obstacle_height) / weather['z0']) / np.log(
            (data_height['v_wind'] - 0.7 * obstacle_height) / weather['z0']))
