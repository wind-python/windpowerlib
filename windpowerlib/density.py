# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:26:19 2017

@author: RL-INSTITUT\sabine.haas
"""

"""
The ``density`` module contains methods
to calculate density (and temperature) at hub height of a wind turbine.
"""


def temperature_gradient(weather, data_height, h_hub):
    r"""
    Calculates the temperature T at hub height assuming a linear temperature
    gradient of -6.5 K/km. This fuction is carried out when the parameter
    'temperature_model' of an object of the class SimpleWindTurbine is
    'temperature_gradient'.

    Parameters
    ----------
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).
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

    References
    ----------
    .. [22] ICAO-Standardatmosphäre (ISA).
        http://www.dwd.de/DE/service/lexikon/begriffe/S/Standardatmosphaere
                _pdf.pdf?__blob=publicationFile&v=3

    todo: check parameters and references
    """
    h_temperature_data = data_height['temp_air']
    return weather.temp_air - 0.0065 * (h_hub - h_temperature_data)


def temperature_interpol(weather, weather_2, data_height, data_height_2,
                         h_hub):
    r"""
    Calculates the temperature T at hub height using an interpolation or
    extrapolation. This fuction is carried out when the parameter
    'temperature_model' of an object of the class SimpleWindTurbine is
    'interpolation'.

    Parameters
    ----------
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    weather_2 : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).
    data_height_2 : dictionary
            Containing the heights of the weather measurements or weather
            model in meters with the keys of the data parameter for a second
            data height
    h_hub : float
        height of the hub of the wind turbine

    Returns
    -------
    pandas.Series
        temperature T in K at hub height

        TODO formula

    """
    h_data_1 = data_height['temp_air']
    h_data_2 = data_height_2['temp_air']
    return (weather_2.temp_air - weather.temp_air) / (h_data_2 - h_data_1) * (
        h_hub - h_data_1) + weather.temp_air


def rho_barometric(weather, data_height, h_hub, T_hub):
    r"""
    Calculates the density of air in kg/m³ at hub height. This fuction is
    carried out when the parameter 'rho_model' of an object of the class
    SimpleWindTurbine is 'barometric'.


    Parameters
    ----------
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).
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

    with T: temperature [K], h: height [m], p: pressure [Pa]

    ToDo: Check the equation and add references.

    References
    ----------
    .. [23] Hau, E. Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit Springer-Verlag, 2008, p. 560
    .. [24] Weitere Erläuterungen zur Druckgradientkraft
        http://www.dwd.de/DE/service/lexikon/begriffe/D/Druckgradient_pdf.
            pdf?__blob=publicationFile&v=4
    """
    h_pressure_data = data_height['pressure']
    return (weather.pressure / 100 - (h_hub - h_pressure_data)
            * 1 / 8) * 1.225 * 288.15 * 100 / (1.0133 * 10**5 * T_hub)


def rho_ideal_gas(weather, data_height, h_hub, T_hub):
    r"""
    Calculates the density of air in kg/m³ at hub height using the ideal gas
    equation. This fuction is carried out when the parameter 'rho_model'
    of an object of the class SimpleWindTurbine is 'ideal_gas'.

    Parameters
    ----------
    weather : DataFrame or Dictionary
            Containing columns or keys with the timeseries for Temperature
            (temp_air), pressure (pressure), wind speed (v_wind) and
            roughness length (z0)
    data_height : DataFrame or Dictionary
            Containing columns or keys with the height of the measurement or
            model data for temperature (temp_air), wind speed (v_wind)
            and pressure (pressure).
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

    with T: temperature [K], h: height [m], p: pressure [Pa]

    ToDo: Check the equation and add references.

    References
    ----------
    .. []
    """
    R_s = 287.058  # J/(kg*k), specific gas constant of dry air
    h_pressure_data = data_height['pressure']
    p_hub = weather.pressure / 100 - (h_hub - h_pressure_data) * 1 / 8
    return p_hub / (R_s * T_hub)
