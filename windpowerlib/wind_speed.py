"""The ``wind_speed`` module contains methods to calculate the wind_speed at
hub height of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"

import numpy as np


def logarithmic_wind_profile(v_wind, v_wind_height, hub_height, z_0,
                             obstacle_height=0):
    r"""
    Calculates the wind speed at hub height.

    The logarithmic height equation is used. There is the possibility of
    including the height of the surrounding obstacles in the calculation.

    Parameters
    ----------
    v_wind : pandas.Series or array
        wind speed time series
    v_wind_height : float
        height for which the corresponding parameter in `v_wind` applies
    hub_height : float
        hub height of wind turbine
    z_0 : pandas.Series or array or float
        roughness length
    obstacle_height : float
        height of obstacles in the surroundings of the wind turbine;
        put obstacle_height to zero for wide spread obstacles

    Returns
    -------
    pandas.Series or array
        wind speed at hub height as time series

    Notes
    -----
    The following equation is used for the logarithmic wind profile [27]_:
    .. math:: v_{wind,hub}=v_{wind,data}\cdot
        \frac{\ln\left(\frac{h_{hub}-d}{z_{0}}\right)}{\ln\left(
        \frac{h_{data}-d}{z_{0}}\right)}

    with:
        v: wind speed, h: height, :math:`z_{0}`: roughness length
        d: includes obstacle height (d = 0.7 * obstacle_height)

    For  d = 0 it results in the following equation [20], [25]_:
    .. math:: v_{wind,hub}=v_{wind,data}\cdot\frac{\ln\left(\frac{h_{hub}}
        {z_{0}}\right)}{\ln\left(\frac{h_{data}}{z_{0}}\right)}

    :math:`h_{data}` is the height in which the wind speed
    :math:`v_{wind,data}` is measured.

    `v_wind_height`, `z_0`, `hub_height` and `obstacle_height` have to be of
    the same unit.

    References
    ----------
    .. [20] Gasch R., Twele J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, page 129
    .. [25] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 515
    .. [27] Quaschning V.: "Regenerative Energiesysteme". München, Hanser
            Verlag, 2011, p. 245
    """
    if 0.7 * obstacle_height > v_wind_height:
        raise ValueError('To take an obstacle height of ' +
                         str(obstacle_height) + ' m into consideration wind ' +
                         'speed data of a higher height is needed.')
    return (v_wind * np.log((hub_height - 0.7 * obstacle_height) / z_0) /
            np.log((v_wind_height - 0.7 * obstacle_height) / z_0))
