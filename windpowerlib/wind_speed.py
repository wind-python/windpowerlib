"""
The ``wind_speed`` module contains functions to calculate the wind speed at
hub height of a wind turbine.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import pandas as pd


def logarithmic_profile(wind_speed, wind_speed_height, hub_height,
                        roughness_length, obstacle_height=0.0):
    r"""
    Calculates the wind speed at hub height using a logarithmic wind profile.

    The logarithmic height equation is used. There is the possibility of
    including the height of the surrounding obstacles in the calculation. This
    function is carried out when the parameter `wind_speed_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'logarithmic'.

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed time series.
    wind_speed_height : float
        Height for which the parameter `wind_speed` applies.
    hub_height : float
        Hub height of wind turbine.
    roughness_length : :pandas:`pandas.Series<series>` or numpy.array or float
        Roughness length.
    obstacle_height : float
        Height of obstacles in the surrounding area of the wind turbine. Set
        `obstacle_height` to zero for wide spread obstacles. Default: 0.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height. Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used [1]_ [2]_ [3]_:

    .. math:: v_{wind,hub}=v_{wind,data}\cdot
        \frac{\ln\left(\frac{h_{hub}-d}{z_{0}}\right)}{\ln\left(
        \frac{h_{data}-d}{z_{0}}\right)}

    with:
        v: wind speed, h: height, :math:`z_{0}`: roughness length,
        d: boundary layer offset (estimated by d=0.7 * `obstacle_height`)

    For  d=0 it results in the following equation [2]_ [3]_:

    .. math:: v_{wind,hub}=v_{wind,data}\cdot\frac{\ln\left(\frac{h_{hub}}
        {z_{0}}\right)}{\ln\left(\frac{h_{data}}{z_{0}}\right)}

    :math:`h_{data}` is the height at which the wind speed
    :math:`v_{wind,data}` is measured and :math:`v_{wind,hub}` is the wind
    speed at hub height :math:`h_{hub}` of the wind turbine.

    Parameters `wind_speed_height`, `roughness_length`, `hub_height` and
    `obstacle_height` have to be of the same unit.

    References
    ----------
    .. [1] Quaschning V.: "Regenerative Energiesysteme". München, Hanser
            Verlag, 2011, p. 278
    .. [2] Gasch, R., Twele, J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, p. 129
    .. [3] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 515

    """
    if 0.7 * obstacle_height > wind_speed_height:
        raise ValueError(
            "To take an obstacle height of {0} m ".format(obstacle_height)
            + "into consideration, wind "
            + "speed data of a greater height is needed."
        )
    # Return np.array if wind_speed is np.array
    if isinstance(wind_speed, np.ndarray) and isinstance(
        roughness_length, pd.Series
    ):
        roughness_length = np.array(roughness_length)

    return (
        wind_speed
        * np.log((hub_height - 0.7 * obstacle_height) / roughness_length)
        / np.log(
            (wind_speed_height - 0.7 * obstacle_height) / roughness_length
        )
    )


def hellman(
    wind_speed,
    wind_speed_height,
    hub_height,
    roughness_length=None,
    hellman_exponent=None,
):
    r"""
    Calculates the wind speed at hub height using the hellman equation.

    It is assumed that the wind profile follows a power law. This function is
    carried out when the parameter `wind_speed_model` of an instance of
    the :class:`~.modelchain.ModelChain` class is 'hellman'.

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed time series.
    wind_speed_height : float
        Height for which the parameter `wind_speed` applies.
    hub_height : float
        Hub height of wind turbine.
    roughness_length : :pandas:`pandas.Series<series>` or numpy.array or float
        Roughness length. If given and `hellman_exponent` is None:
        `hellman_exponent`=1 / ln(hub_height/roughness_length),
        otherwise `hellman_exponent`=1/7. Default: None.
    hellman_exponent : None or float
        The Hellman exponent, which combines the increase in wind speed due to
        stability of atmospheric conditions and surface roughness into one
        constant. If None and roughness length is given
        `hellman_exponent`=1 / ln(hub_height/roughness_length),
        otherwise `hellman_exponent`=1/7. Default: None.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height. Data type depends on type of `wind_speed`.

    Notes
    -----
    The following equation is used [1]_ [2]_ [3]_:

    .. math:: v_{wind,hub}=v_{wind,data}\cdot \left(\frac{h_{hub}}{h_{data}}
        \right)^\alpha

    with:
        v: wind speed, h: height, :math:`\alpha`: Hellman exponent

    :math:`h_{data}` is the height in which the wind speed
    :math:`v_{wind,data}` is measured and :math:`v_{wind,hub}` is the wind
    speed at hub height :math:`h_{hub}` of the wind turbine.

    For the Hellman exponent :math:`\alpha` many studies use a value of 1/7 for
    onshore and a value of 1/9 for offshore. The Hellman exponent can also
    be calulated by the following equation [2]_ [3]_:

    .. math:: \alpha=\frac{1}{\ln\left(\frac{h_{hub}}{z_0} \right)}

    with:
        :math:`z_{0}`: roughness length

    Parameters `wind_speed_height`, `roughness_length`, `hub_height` and
    `obstacle_height` have to be of the same unit.

    References
    ----------
    .. [1] Sharp, E.: "Spatiotemporal disaggregation of GB scenarios depicting
            increased wind capacity and electrified heat demand in dwellings".
            UCL, Energy Institute, 2015, p. 83
    .. [2] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 517
    .. [3] Quaschning V.: "Regenerative Energiesysteme". München, Hanser
            Verlag, 2011, p. 279

    """
    if hellman_exponent is None:
        if roughness_length is not None:
            # Return np.array if wind_speed is np.array
            if isinstance(wind_speed, np.ndarray) and isinstance(
                roughness_length, pd.Series
            ):
                roughness_length = np.array(roughness_length)
            hellman_exponent = 1 / np.log(hub_height / roughness_length)
        else:
            hellman_exponent = 1 / 7
    return wind_speed * (hub_height / wind_speed_height) ** hellman_exponent
