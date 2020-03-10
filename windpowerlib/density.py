"""
The ``density`` module contains functions to calculate the density and
temperature at hub height of a wind turbine.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""


def barometric(pressure, pressure_height, hub_height, temperature_hub_height):
    r"""
    Calculates the density of air at hub height using the barometric height
    equation.

    This function is carried out when the parameter `density_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'barometric'.

    Parameters
    ----------
    pressure : :pandas:`pandas.Series<series>` or numpy.array
        Air pressure in Pa.
    pressure_height : float
        Height in m for which the parameter `pressure` applies.
    hub_height : float
        Hub height of wind turbine in m.
    temperature_hub_height : :pandas:`pandas.Series<series>` or numpy.array
        Air temperature at hub height in K.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Density of air at hub height in kg/m³.
        Returns a pandas.Series if one of the input parameters is a
        pandas.Series.

    Notes
    -----

    The following equation is used [1]_ [2]_ :

    .. math:: \rho_{hub}=\left(p/100-\left(h_{hub}-h_{p,data}\right)
       \cdot\frac{1}{8}\right)\cdot \frac{\rho_0 T_0\cdot 100}{p_0 T_{hub}}

    with:
        T: temperature [K], h: height [m], :math:`\rho`: density [kg/m³],
        p: pressure [Pa]

    :math:`h_{p,data}` is the height of the measurement or model data for
    pressure, :math:`p_0` the ambient air pressure, :math:`\rho_0` the ambient
    density of air, :math:`T_0` the ambient temperature and :math:`T_{hub}` the
    temperature at hub height :math:`h_{hub}`.

    Assumptions:

    * Pressure gradient of -1/8 hPa/m

    References
    ----------
    .. [1] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 560
    .. [2] Deutscher Wetterdienst:
        http://www.dwd.de/DE/service/lexikon/begriffe/D/Druckgradient_pdf.pdf?__blob=publicationFile&v=4

    """
    return (
        (pressure / 100 - (hub_height - pressure_height) * 1 / 8)
        * 1.225
        * 288.15
        * 100
        / (101330 * temperature_hub_height)
    )


def ideal_gas(pressure, pressure_height, hub_height, temperature_hub_height):
    r"""
    Calculates the density of air at hub height using the ideal gas equation.

    This function is carried out when the parameter `density_model` of an
    instance of the :class:`~.modelchain.ModelChain` class is 'ideal_gas'.

    Parameters
    ----------
    pressure : :pandas:`pandas.Series<series>` or numpy.array
        Air pressure in Pa.
    pressure_height : float
        Height in m for which the parameter `pressure` applies.
    hub_height : float
        Hub height of wind turbine in m.
    temperature_hub_height : :pandas:`pandas.Series<series>` or numpy.array
        Air temperature at hub height in K.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Density of air at hub height in kg/m³.
        Returns a pandas.Series if one of the input parameters is a
        pandas.Series.

    Notes
    -----
    The following equations are used [1]_ [2]_ [3]_:

    .. math:: \rho_{hub}=p_{hub}/ (R_s T_{hub})

    and [4]_:

    .. math:: p_{hub}=\left(p/100-\left(h_{hub}-h_{p,data}\right)\cdot
              \frac{1}{8}\right)\cdot 100

    with:
        T: temperature [K], :math:`\rho`: density [kg/m³], p: pressure [Pa]

    :math:`h_{p,data}` is the height of the measurement or model data for
    pressure, :math:`R_s` is the specific gas constant of dry air
    (287.058 J/(kg*K)) and :math:`p_{hub}` is the pressure at hub height
    :math:`h_{hub}`.

    References
    ----------
    .. [1] Ahrendts J., Kabelac S.: "Das Ingenieurwissen - Technische
            Thermodynamik". 34. Auflage, Springer-Verlag, 2014, p. 23
    .. [2] Biank, M.: "Methodology, Implementation and Validation of a
            Variable Scale Simulation Model for Windpower based on the
            Georeferenced Installation Register of Germany". Master's Thesis
            at RLI, 2014, p. 57
    .. [3] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
            Windenergieeinspeisung für wetterdatenbasierte
            Windleistungssimulationen". Universität Kassel, Diss., 2016, p. 97
    .. [4] Deutscher Wetterdienst:
            http://www.dwd.de/DE/service/lexikon/begriffe/D/Druckgradient_pdf.pdf?__blob=publicationFile&v=4

    """
    return (
        (pressure / 100 - (hub_height - pressure_height) * 1 / 8)
        * 100
        / (287.058 * temperature_hub_height)
    )
