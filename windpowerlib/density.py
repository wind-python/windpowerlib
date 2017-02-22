"""
The ``density`` module contains methods to calculate the density and
temperature at hub height of a wind turbine.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


def temperature_gradient(temp_air, temp_height, hub_height):
    r"""
    Calculates the temperature at hub height using a linear temperature 
    gradient.

    A linear temperature gradient of -6.5 K/km is assumed. This function is
    carried out when the parameter `temperature_model` of an instance of
    the :class:`windpowerlib.wind_turbine.WindTurbine` class is 
    'temperature_gradient'.

    Parameters
    ----------
    temp_air : pandas.Series or array
        Air temperature time series in K.
    temp_height : float
        Height in m for which the parameter `temp_air` applies.
    hub_height : float
        Hub height of wind turbine in m.

    Returns
    -------
    pandas.Series or array
        Temperature at hub height in K.

    Notes
    -----

    The following equation is used [22]_:
    
    .. math:: T_{hub}=T_{air}-0.0065\cdot\left(h_{hub}-h_{T,data}\right)

    with:
        T: temperature [K], h: height [m]

    :math:`h_{T,data}` is the height in which the temperature is measured.

    Assumptions:
    
    * Temperature gradient of -6.5 K/km (-0.0065 K/m)
        
    References
    ----------
    .. [22] ICAO-Standardatmosphäre (ISA).
        http://www.dwd.de/DE/service/lexikon/begriffe/S/Standardatmosphaere_pdf.pdf?__blob=publicationFile&v=3

    """
    return temp_air - 0.0065 * (hub_height - temp_height)


def temperature_interpol(temp_air_1, temp_air_2, 
                         temp_air_height_1, temp_air_height_2, hub_height):
    r"""
    Calculates the temperature at hub height by inter- or extrapolation.

    This fuction is carried out when the parameter `temperature_model` of an
    an instance of the :class:`windpowerlib.wind_turbine.WindTurbine` class
    is 'interpolation'.

    Parameters
    ----------
    temp_air_1 : pandas.Series or array
        Air temperature time series.
    temp_air_2 : pandas.Series or array
        Second air temperature time series for interpolation.
    temp_air_height_1 : float
        Height for which the parameter `temp_air_1` applies.
    temp_air_height_2 : float
        Height for which the parameter `temp_air_2` applies.
    hub_height : float
        Hub height of wind turbine in m.

    Returns
    -------
    pandas.Series or array
        Temperature at hub height.

    Notes
    -----

    The following equation is used:
    
    .. math:: T_{hub} = (T_2 - T_1) / (h_2 - h_1) * (h_{hub} - h_1) + T_1

    with:
        T: temperature, h: height

    Assumptions:
    
    * linear temperature gradient
    
    """
    return ((temp_air_2 - temp_air_1) / 
            (temp_air_height_2 - temp_air_height_1) *
            (hub_height - temp_air_height_1) + temp_air_1)


def rho_barometric(pressure, pressure_height, hub_height, T_hub):
    r"""
    Calculates the density of air at hub height by barometric height equation.

    This fuction is carried out when the parameter `rho_model` of an instance 
    of the :class:`windpowerlib.wind_turbine.WindTurbine` class is 
    'barometric'.

    Parameters
    ----------
    pressure : pandas.Series or array
        Pressure time series in Pa.
    pressure_height : float
        Height in m for which the parameter `pressure` applies.
    hub_height : float
        Hub height of wind turbine in m.
    T_hub : pandas.Series or array
        Temperature at hub height in K.

    Returns
    -------
    pandas.Series
        Density of air at hub height in kg/m³.

    Notes
    -----
    
    The following equation is used [23]_, [24]_ :
    
    .. math:: \rho_{hub}=\left(p/100-\left(h_{hub}-h_{p,data}\right)
       \cdot\frac{1}{8}\right)\cdot \frac{\rho_0 T_0\cdot 100}{p_0 T_{hub}}


    with:
        T: temperature [K], h: height [m], :math:`\rho`: density [kg/m³],
        p: pressure [Pa]

    :math:`h_{p,data}` is the height of the measurement or model data for
    pressure, :math:`p_0` the ambient air pressure, :math:`\rho_0` the ambient
    density of air, :math:`T_0` the ambient temperature and :math:`T_{hub}` the
    temperature at hub height.
    
    Assumptions:
    
    * Pressure gradient of -1/8 hPa/m

    References
    ----------
    .. [23] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 560
    .. [24] Deutscher Wetterdienst
        http://www.dwd.de/DE/service/lexikon/begriffe/D/Druckgradient_pdf.pdf?__blob=publicationFile&v=4

    """
    return ((pressure / 100 - (hub_height - pressure_height) * 1 / 8) * 1.225 *
            288.15 * 100 / (101330 * T_hub))


def rho_ideal_gas(pressure, pressure_height, hub_height, T_hub):
    r"""
    Calculates the density of air at hub height using the ideal gas equation.

    This fuction is carried out when the parameter `rho_model` of an instance 
    of the :class:`windpowerlib.wind_turbine.WindTurbine` class is 'ideal_gas'.

    Parameters
    ----------
    pressure : pandas.Series or array
        Pressure time series in Pa.
    pressure_height : float
        Height in m for which the parameter `pressure` applies.
    hub_height : float
        Hub height of wind turbine in m.
    T_hub : pandas.Series or array
        Temperature at hub height in K.

    Returns
    -------
    pandas.Series
        Density of air at hub height in kg/m³.

    Notes
    -----
    The following equations are used:
    
    .. math:: \rho_{hub}=p_{hub}/ (R_s T_{hub})
    .. math:: p_{hub}=\left(p/100-\left(h_{hub}-h_{p,data}\right)\cdot
              \frac{1}{8}\right)\cdot 100
    (see also :function:`density.rho_barometric`

    with:
        T: temperature [K], :math:`\rho`: density [kg/m³], p: pressure [Pa]

    :math:`R_s` is the specific gas constant of dry air (287.058 J/(kg*K)) and
    :math:`p_{hub}` is the pressure at hub height.

    ToDo: Check equation and add references for ideal gas equation

    """
    return ((pressure / 100 - (hub_height - pressure_height) * 1 / 8) * 100 /
            (287.058 * T_hub))
