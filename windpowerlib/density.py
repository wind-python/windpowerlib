"""The ``density`` module contains methods to calculate the density and
temperature at hub height of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"
__author__ = "author1, author2"


def temperature_gradient(temp_air, temp_height, h_hub):
    r"""
    Calculates the temperature T at hub height assuming a linear temperature
    gradient of -6.5 K/km. This fuction is carried out when the parameter
    'temperature_model' of an object of the class SimpleWindTurbine is
    'temperature_gradient'.

    Parameters
    ----------
    temp_air : pandas.Series or array
        air temperature in K
    temp_height : float
        height of the measurement or model data for temperature in m
    h_hub : float
        height of the hub of the wind turbine

    Returns
    -------
    pandas.Series
        temperature T in K at hub height

    Notes
    -----
    Assumptions:
        * Temperature gradient of -6.5 K/km

    The following equation is used [22]_:
    .. math:: T_{hub}=T_{air, data}-0.0065\cdot\left(h_{hub}-h_{T,data}\right)

    with:
        T: temperature [K], h: height [m]

    :math:`h_{data}` is the height in which the temperature is measured.
    (height in m, temperature in K)

    References
    ----------
    .. [22] ICAO-Standardatmosphäre (ISA).
        http://www.dwd.de/DE/service/lexikon/begriffe/S/Standardatmosphaere
                _pdf.pdf?__blob=publicationFile&v=3
    """
    return temp_air - 0.0065 * (h_hub - temp_height)


def temperature_interpol(temp_air_1, temp_air_2, temp_height_1, temp_height_2,
                         h_hub):
    r"""
    Calculates the temperature T at hub height using an interpolation or
    extrapolation. This fuction is carried out when the parameter
    'temperature_model' of an object of the class SimpleWindTurbine is
    'interpolation'.

    Parameters
    ----------
    temp_air_1 : pandas.Series or array
        air temperature
    temp_air_2 : pandas.Series or array
        air temperature
    temp_height_1 : float
        height of the measurement or model data for temperature for the
        temperature set of `temp_air_1`
    temp_height_2 : float
        height of the measurement or model data for temperature for the
        temperature set of `temp_air_2`
    h_hub : float
        height of the hub of the wind turbine

    Returns
    -------
    pandas.Series
        temperature T in K at hub height

    Notes
    -----
    Assumptions:
        * linear temperature gradient

    Linear interpolation of the temperature is used:
    .. math:: T_{hub} = (T_2 - T_1) / (h_2 - h_1) * (h_{hub} - h_1) + T_1

    with:
        T: temperature [K], h: height [m]

    :math:`h_{data}` is the height in which the temperature is measured.
    (height in m, temperature in K)
    """
    return ((temp_air_2 - temp_air_1) / (temp_height_2 - temp_height_1) *
            (h_hub - temp_height_1) + temp_air_1)


def rho_barometric(pressure, pressure_height, h_hub, T_hub):
    r"""
    Calculates the density of air in kg/m³ at hub height. This fuction is
    carried out when the parameter 'rho_model' of an object of the class
    SimpleWindTurbine is 'barometric'.


    Parameters
    ----------
    pressure : pandas.Series or array
        pressure in Pa
    pressure_height : float
        height of the measurement or model data for pressure in m
    h_hub : float
        hub height of wind turbine in m
    T_hub : pandas.Series
        temperature in K at hub height

    Returns
    -------
    pandas.Series
        density of air in kg/m³ at hub height

    Notes
    -----
    Assumptions:
      * Pressure gradient of -1/8 hPa/m

    The following equation is used [23],[24]_:
    .. math:: \rho_{hub}=\left(p_{data}/100-\left(h_{hub}-h_{p,data}\right)
       \cdot\frac{1}{8}\right)\cdot \frac{\rho_0 T_0\cdot 100}{p_0 T_{hub}}

    with:
        T: temperature [K], h: height [m], :math:`\rho`: density [kg/m³],
        p: pressure [Pa]

    :math:`h_{data}` is the height in which the temperature is measured.
    (height in m)
    :math:`p_0` is the ambient air pressure.

    References
    ----------
    .. [23] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 560
    .. [24] Weitere Erläuterungen zur Druckgradientkraft
        http://www.dwd.de/DE/service/lexikon/begriffe/D/Druckgradient_pdf.
            pdf?__blob=publicationFile&v=4
    """
    return ((pressure / 100 - (h_hub - pressure_height) * 1 / 8) * 1.225 *
            288.15 * 100 / (101330 * T_hub))


def rho_ideal_gas(pressure, pressure_height, h_hub, T_hub):
    r"""
    Calculates the density of air in kg/m³ at hub height using the ideal gas
    equation. This fuction is carried out when the parameter 'rho_model'
    of an object of the class SimpleWindTurbine is 'ideal_gas'.

    Parameters
    ----------
    pressure : pandas.Series or array
        pressure in Pa
    pressure_height : float
        height of the measurement or model data for pressure in m
    h_hub : float
        hub height of wind turbine in m
    T_hub : pandas.Series
        temperature in K at hub height

    Returns
    -------
    pandas.Series
        density of air in kg/m³ at hub height

    Notes
    -----
    The following equation is used []_:
    .. math:: \rho_{hub}=p_{hub}/ (R_s T_{hub})

    with:
        T: temperature [K], :math:`\rho`: density [kg/m³], p: pressure [Pa]
        :math:`R_s`: specific gas constant  of dry air [J/(kg*K)]

    ToDo: Check equation and add references

    References
    ----------
    .. []
    """
    return ((pressure / 100 - (h_hub - pressure_height) * 1 / 8) * 100 /
            (287.058 * T_hub))
