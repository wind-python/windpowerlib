"""
The ``temperature`` module contains functions to calculate the temperature at
hub height of a wind turbine.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""


def linear_gradient(temperature, temperature_height, hub_height):
    r"""
    Calculates the temperature at hub height using a linear gradient.

    A linear temperature gradient of -6.5 K/km is assumed. This function is
    carried out when the parameter `temperature_model` of an instance of
    the :class:`~.modelchain.ModelChain` class is
    'temperature_gradient'.

    Parameters
    ----------
    temperature : :pandas:`pandas.Series<series>` or numpy.array
        Air temperature in K.
    temperature_height : float
        Height in m for which the parameter `temperature` applies.
    hub_height : float
        Hub height of wind turbine in m.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Temperature at hub height in K.

    Notes
    -----

    The following equation is used [1]_:

    .. math:: T_{hub}=T_{air}-0.0065\cdot\left(h_{hub}-h_{T,data}\right)

    with:
        T: temperature [K], h: height [m]

    :math:`h_{T,data}` is the height in which the temperature :math:`T_{air}`
    is measured and :math:`T_{hub}` is the temperature at hub height
    :math:`h_{hub}` of the wind turbine.

    Assumptions:

    * Temperature gradient of -6.5 K/km (-0.0065 K/m)

    References
    ----------
    .. [1] ICAO-Standardatmosphäre (ISA).
        http://www.dwd.de/DE/service/lexikon/begriffe/S/Standardatmosphaere_pdf.pdf?__blob=publicationFile&v=3

    """
    return temperature - 0.0065 * (hub_height - temperature_height)
