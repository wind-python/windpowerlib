"""
The ``power_output`` module contains functions to calculate the power output
of a wind turbine.

"""

import numpy as np
import pandas as pd

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


def cp_curve(v_wind, rho_hub, d_rotor, cp_values):
    r"""
    Calculates the turbine power output using a cp curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class
    is 'cp_values' and the parameter `density_corr` is False.

    Parameters
    ----------
    v_wind : pandas.Series or array
        Wind speed at hub height in m/s.
    rho_hub : pandas.Series or array
        Density of air at hub height in kg/m³.
    d_rotor : float
        Diameter of rotor in m.
    cp_values : pandas.DataFrame
        Power coefficient curve of the wind turbine.
        Indices are the wind speeds of the power coefficient curve in m/s, the
        corresponding power coefficient values are in the column 'cp'.

    Returns
    -------
    pandas.Series
        Electrical power output of the wind turbine in W.

    Notes
    -----
    The following equation is used [1]_, [2]_:

    .. math:: P=\frac{1}{8}\cdot\rho_{hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        P: power [W], :math:`\rho`: density [kg/m³], d: diameter [m],
        v: wind speed [m/s], cp: power coefficient

    It is assumed that the power output for wind speeds above the maximum
    wind speed given in the power coefficient curve is zero.

    References
    ----------
    .. [1] Gasch, R., Twele, J.: "Windkraftanlagen". 6. Auflage, Wiesbaden,
            Vieweg + Teubner, 2010, pages 35ff, 208
    .. [2] Hau, E.: "Windkraftanlagen - Grundlagen, Technik, Einsatz,
            Wirtschaftlichkeit". 4. Auflage, Springer-Verlag, 2008, p. 542

    """
    # cp time series
    # TODO introduce new parameter v_cutout to allow for power output above
    # maximum wind speed from power coefficient curve (maximum power output
    # must be limited)
    cp_series = np.interp(v_wind, cp_values.index, cp_values.cp,
                          left=0, right=0)
    return (1 / 8 * rho_hub * d_rotor ** 2 * np.pi * np.power(v_wind, 3) *
            cp_series)


def cp_curve_density_corr(v_wind, rho_hub, d_rotor, cp_values):
    r"""
    Calculates the turbine power output using a density corrected cp curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class
    is 'cp_values' and the parameter `density_corr` is True.

    Parameters
    ----------
    v_wind : pandas.Series or array
        Wind speed at hub height in m/s.
    rho_hub : pandas.Series or array
        Density of air at hub height in kg/m³.
    cp_values : pandas.DataFrame
        Power coefficient curve of the wind turbine.
        Indices are the wind speeds of the power coefficient curve in m/s, the
        corresponding power coefficient values are in the column 'cp'.
    d_rotor : float
        Diameter of the rotor in m.

    Returns
    -------
    pandas.Series
        Electrical power of the wind turbine in W.

    Notes
    -----
    See :py:func:`cp_curve` for further information on how the power values
    are calculated and :py:func:`p_curve_density_corr` for further
    information on how the density correction is implemented.

    It is assumed that the power output for wind speeds above the maximum
    wind speed given in the power coefficient curve is zero.

    """
    p_values = (1 / 8 * 1.225 * d_rotor ** 2 * np.pi *
                np.power(cp_values.index, 3) * cp_values.cp)
    p_values = pd.DataFrame(data=np.array(p_values), index=cp_values.index,
                            columns=['P'])
    return p_curve_density_corr(v_wind, rho_hub, p_values)


def p_curve(p_values, v_wind):
    r"""
    Calculates the turbine power output using a power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class is 'p_values' and
    the parameter `density_corr` is False.

    Parameters
    ----------
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        Indices are the wind speeds of the power curve in m/s, the
        corresponding power values in W are in the column 'P'.
    v_wind : pandas.Series or array
        Wind speed at hub height in m/s.

    Returns
    -------
    power_output : pandas.Series
        Electrical power output of the wind turbine in W.

    Notes
    -------
    It is assumed that the power output for wind speeds above the maximum
    wind speed given in the power curve is zero.

    """
    # TODO introduce new parameter v_cutout to allow for power output above
    # maximum wind speed from power curve
    power_output = np.interp(v_wind, p_values.index, p_values.P,
                             left=0, right=0)
    # Set index for time series
    try:
        series_index = v_wind.index
    except AttributeError:
        series_index = range(1, len(power_output)+1)
    power_output = pd.Series(data=power_output, index=series_index,
                             name='feedin_wind_turbine')
    return power_output


def p_curve_density_corr(v_wind, rho_hub, p_values):
    r"""
    Calculates the turbine power output using a density corrected power curve.

    This function is carried out when the parameter `power_output_model` of an
    instance of the :class:`~.modelchain.Modelchain` class is 'p_values' and
    the parameter `density_corr` is True.

    Parameters
    ----------
    v_wind : pandas.Series or array
        Wind speed time series at hub height in m/s.
    rho_hub : pandas.Series or array
        Density of air at hub height in kg/m³.
    p_values : pandas.DataFrame
        Power curve of the wind turbine.
        The indices are the corresponding wind speeds of the power curve, the
        power values containing column is called 'P'.

    Returns
    -------
    power_output : pandas.Series
        Electrical power output of the wind turbine in W.

    Notes
    -----
    The following equation is used for the wind speed at site
    [1]_, [2]_, [3]_:

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

    :math:`v_{std}` is the standard wind speed in the power curve
    (:math:`v_{std}`, :math:`P_{std}`).
    :math:`v_{site}` is the density corrected wind speed for the power curve
    (:math:`v_{site}`, :math:`P_{std}`).

    It is assumed that the power output for wind speeds above the maximum
    wind speed given in the power curve is zero.

    References
    ----------
    .. [1] Svenningsen, L.: "Power Curve Air Density Correction And Other
            Power Curve Options in WindPRO". 1st edition, Aalborg,
            EMD International A/S , 2010, p. 4
    .. [2] Svenningsen, L.: "Proposal of an Improved Power Curve Correction".
            EMD International A/S , 2010
    .. [3] Biank, M.: "Methodology, Implementation and Validation of a
            Variable Scale Simulation Model for Windpower based on the
            Georeferenced Installation Register of Germany". Master's Thesis
            at Reiner Lemoine Institute, 2014, p. 13

    """
    # TODO introduce new parameter v_cutout to allow for power output above
    # maximum wind speed from power curve
    power_output = [(np.interp(v_wind[i],
                               p_values.index * (1.225 / rho_hub[i])**(
                                   np.interp(p_values.index,
                                             [7.5, 12.5], [1/3, 2/3])),
                               p_values.P, left=0, right=0))
                    for i in range(len(v_wind))]

    # Set index for time series
    try:
        series_index = v_wind.index
    except AttributeError:
        series_index = range(1, len(power_output)+1)
    power_output = pd.Series(data=power_output, index=series_index,
                             name='feedin_wind_turbine')
    return power_output
