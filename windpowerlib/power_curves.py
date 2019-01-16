"""
The ``power_curves`` module contains functions for applying alterations like
power curve smoothing or reducing power values by an efficiency to the power
curve of a wind turbine, wind farm or wind turbine cluster.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import os
from collections import namedtuple
import numpy as np
import pandas as pd
from windpowerlib import tools


def smooth_power_curve(power_curve_wind_speeds, power_curve_values,
                       block_width=0.5, wind_speed_range=15.0,
                       standard_deviation_method='turbulence_intensity',
                       mean_gauss=0, **kwargs):
    r"""
    Smooths the input power curve values by using a Gauss distribution.

    The smoothing serves for taking the distribution of wind speeds over space
    into account.

    Parameters
    ----------
    power_curve_wind_speeds : pandas.Series or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    block_width : float
        Width between the wind speeds in the sum of equation :eq:`power`.
        Default: 0.5.
    wind_speed_range : float
        The sum in the equation below is taken for this wind speed range below
        and above the power curve wind speed. Default: 15.0.
    standard_deviation_method : string
        Method for calculating the standard deviation for the Gauss
        distribution. Options: 'turbulence_intensity', 'Staffell_Pfenninger'.
        Default: 'turbulence_intensity'.
    mean_gauss : float
        Mean of the Gauss distribution in
        :py:func:`~.tools.gauss_distribution`. Default: 0.

    Other Parameters
    ----------------
    turbulence intensity : float, optional
        Turbulence intensity at hub height of the wind turbine, wind farm or
        wind turbine cluster the power curve is smoothed for.

    Returns
    -------
    smoothed_power_curve_df : pd.DataFrame
        Smoothed power curve. DataFrame has 'wind_speed' and 'power' columns
        with wind speeds in m/s and the corresponding power curve value in W.

    Notes
    -----
    The following equation is used to calculated the power curves values of the
    smoothed power curve [1]_:

    .. math:: P_{smoothed}(v_{std}) = \sum\limits_{v_i} \Delta v_i \cdot P(v_i)
        \cdot \frac{1}{\sigma \sqrt{2 \pi}}
        \exp \left[-\frac{(v_{std} - v_i -\mu)^2}{2 \sigma^2} \right]
       :label: power

    with:
        P: power [W], v: wind speed [m/s],
        :math:`\sigma`: standard deviation (Gauss), :math:`\mu`: mean (Gauss)

        :math:`P_{smoothed}` is the smoothed power curve value,
        :math:`v_{std}` is the standard wind speed in the power curve,
        :math:`\Delta v_i` is the interval length between
        :math:`v_\text{i}` and :math:`v_\text{i+1}`

    Power curve smoothing is applied to take account for the spatial
    distribution of wind speed. This way of smoothing power curves is also used
    in [2]_ and [3]_.

    The standard deviation :math:`\sigma` of the above equation can be
    calculated by the following methods.

    'turbulence_intensity' [2]_:

    .. math:: \sigma = v_\text{std} \sigma_\text{n} = v_\text{std} TI

    with:
        TI: turbulence intensity

    'Staffell_Pfenninger' [4]_:

    .. math:: \sigma = 0.6 \cdot 0.2 \cdot v_\text{std}

    References
    ----------
    .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 106
    .. [2]  Nørgaard, P. and Holttinen, H.: "A Multi-Turbine and Power Curve
             Approach". Nordic Wind Power Conference, 1.–2.3.2004, 2000, p. 5
    .. [3]  Kohler, S. and Agricola, A.-Cl. and Seidl, H.:
             "dena-Netzstudie II. Integration erneuerbarer Energien in die
             deutsche Stromversorgung im Zeitraum 2015 – 2020 mit Ausblick
             2025". Technical report, 2010.
    .. [4]  Staffell, I. and Pfenninger, S.: "Using Bias-Corrected Reanalysis
              to Simulate Current and Future Wind Power Output". 2005, p. 11

    """
    # Specify normalized standard deviation
    if standard_deviation_method == 'turbulence_intensity':
        if ('turbulence_intensity' in kwargs and
                kwargs['turbulence_intensity'] is not np.nan):
            normalized_standard_deviation = kwargs['turbulence_intensity']
        else:
            raise ValueError("Turbulence intensity must be defined for " +
                             "using 'turbulence_intensity' as " +
                             "`standard_deviation_method`")
    elif standard_deviation_method == 'Staffell_Pfenninger':
        normalized_standard_deviation = 0.2
    else:
        raise ValueError("{} is no valid `standard_deviation_method`. Valid "
                         + "options are 'turbulence_intensity', or "
                         + "'Staffell_Pfenninger'".format(
            standard_deviation_method))
    # Initialize list for power curve values
    smoothed_power_curve_values = []
    # Append wind speeds to `power_curve_wind_speeds`
    maximum_value = power_curve_wind_speeds.values[-1] + wind_speed_range
    while power_curve_wind_speeds.values[-1] < maximum_value:
        power_curve_wind_speeds = power_curve_wind_speeds.append(
            pd.Series(power_curve_wind_speeds.iloc[-1] + 0.5,
                      index=[power_curve_wind_speeds.index[-1] + 1]))
        power_curve_values = power_curve_values.append(
            pd.Series(0.0, index=[power_curve_values.index[-1] + 1]))
    for power_curve_wind_speed in power_curve_wind_speeds:
        # Create array of wind speeds for the sum
        wind_speeds_block = (np.arange(
            -wind_speed_range, wind_speed_range + block_width, block_width) +
            power_curve_wind_speed)
        # Get standard deviation for Gauss function
        standard_deviation = (
            (power_curve_wind_speed * normalized_standard_deviation + 0.6)
            if standard_deviation_method is 'Staffell_Pfenninger'
            else power_curve_wind_speed * normalized_standard_deviation)
        # Get the smoothed value of the power output
        if standard_deviation == 0.0:
            # The gaussian distribution is not defined for a standard deviation
            # of zero. Smoothed power curve value is set to zero.
            smoothed_value = 0.0
        else:
            smoothed_value = sum(
                block_width * np.interp(wind_speed, power_curve_wind_speeds,
                                        power_curve_values, left=0, right=0) *
                tools.gauss_distribution(
                    power_curve_wind_speed - wind_speed,
                    standard_deviation, mean_gauss)
                for wind_speed in wind_speeds_block)
        # Add value to list - add zero if `smoothed_value` is nan as Gauss
        # distribution for a standard deviation of zero.
        smoothed_power_curve_values.append(smoothed_value)
    # Create smoothed power curve data frame
    smoothed_power_curve_df = pd.DataFrame(
        data=[list(power_curve_wind_speeds.values),
              smoothed_power_curve_values]).transpose()
    # Rename columns of the data frame
    smoothed_power_curve_df.columns = ['wind_speed', 'power']
    return smoothed_power_curve_df


def wake_losses_to_power_curve(power_curve_wind_speeds, power_curve_values,
                               wind_farm_efficiency,
                               wake_losses_model='power_efficiency_curve'):
    r"""
    Reduces the power values of a power curve by an efficiency (curve).

    Parameters
    ----------
    power_curve_wind_speeds : pandas.Series or numpy.array
        Wind speeds in m/s for which the power curve values are provided in
        `power_curve_values`.
    power_curve_values : pandas.Series or numpy.array
        Power curve values corresponding to wind speeds in
        `power_curve_wind_speeds`.
    wind_farm_efficiency : float or pd.DataFrame
        Efficiency of the wind farm. Either constant (float) or efficiency
        curve (pd.DataFrame) containing 'wind_speed' and 'efficiency' columns
        with wind speeds in m/s and the corresponding dimensionless wind farm
        efficiency (reduction of power). Default: None.
    wake_losses_model : String
        Defines the method for taking wake losses within the farm into
        consideration. Options: 'power_efficiency_curve',
        'constant_efficiency'. Default: 'power_efficiency_curve'.

    Returns
    -------
    power_curve_df : pd.DataFrame
        Power curve with power values reduced by a wind farm efficiency.
        DataFrame has 'wind_speed' and 'power' columns with wind speeds in m/s
        and the corresponding power curve value in W.

    """
    # Create power curve DataFrame
    power_curve_df = pd.DataFrame(
        data=[list(power_curve_wind_speeds),
              list(power_curve_values)]).transpose()
    # Rename columns of DataFrame
    power_curve_df.columns = ['wind_speed', 'power']
    if wake_losses_model == 'constant_efficiency':
        if not isinstance(wind_farm_efficiency, float):
            raise TypeError("'wind_farm_efficiency' must be float if " +
                            "`wake_losses_model´ is '{}' but is {}".format(
                                wake_losses_model, wind_farm_efficiency))
        power_curve_df['power'] = power_curve_values * wind_farm_efficiency
    elif wake_losses_model == 'power_efficiency_curve':
        if (not isinstance(wind_farm_efficiency, dict) and
                not isinstance(wind_farm_efficiency, pd.DataFrame)):
            raise TypeError(
                "'wind_farm_efficiency' must be pd.DataFrame if " +
                "`wake_losses_model´ is '{}' but is {}".format(
                    wake_losses_model, wind_farm_efficiency))
        df = pd.concat([power_curve_df.set_index('wind_speed'),
                        wind_farm_efficiency.set_index('wind_speed')], axis=1)
        # Add column with reduced power (nan values of efficiency are interpolated)
        df['reduced_power'] = df['power'] * df['efficiency'].interpolate(
            method='index')
        reduced_power = df['reduced_power'].dropna()
        power_curve_df = pd.DataFrame([reduced_power.index,
                                       reduced_power.values]).transpose()
        power_curve_df.columns = ['wind_speed', 'power']
    else:
        raise ValueError(
            "`wake_losses_model` is {} but should be ".format(
                wake_losses_model) +
            "'constant_efficiency' or 'power_efficiency_curve'")
    return power_curve_df


def get_power_curve_from_file(name, filename=None, coefficient_curve=False):
    """
    Get a power curve from a csv file as a named tuple. Fields are

    * windspeed (array)
    * value (power or coefficient) (array)
    * nominal_power (int)

    The csv file has to have a special format. See example file.

    Parameters
    ----------
    name : str
        Type of the turbine (full name)
    filename : str or None
        Full filename of the csv file. If None an internal file will be used.

    Examples
    --------
    >>> data = get_power_curve_from_file('AN BONUS 54')
    >>> data.nominal_power
    1000000
    >>> my_turbine = {
    ...     'name': 'myTurbine',
    ...     'nominal_power': data.nominal_power,
    ...     'hub_height': 105,
    ...     'rotor_diameter': 90,
    ...     'power_curve': pd.DataFrame({'power': data.value,
    ...                                  'wind_speed': data.windspeed})}
    >>> my_turbine['nominal_power']
    1000000
    >>> data2 = get_power_curve_from_file('AN BONUS 54',
    ...                                   coefficient_curve=True)
    >>> int(data.value.mean())
    603777
    >>> int(data2.value.mean() * 100) / 100
    0.19
    
    Returns
    -------
    namedtuple : Fields: windspeed, value, nominal_power

    """
    pwr_curve = namedtuple('power_curve', 'windspeed, value, nominal_power')
    if filename is None:
        if coefficient_curve:
            fn = 'power_coefficient_curves.csv'
        else:
            fn = 'power_curves.csv'

        filename = os.path.join(os.path.dirname(__file__), 'data', fn)
    pc = pd.read_csv(filename, index_col=[1])

    pc.drop(['source', 'modificationtimestamp', 'Unnamed: 0'], axis=1,
            inplace=True)

    p_nom = pc.pop('p_nom')
    pc = pc.unstack().unstack()[name].dropna()
    return pwr_curve(nominal_power=p_nom[name], windspeed=pc.index.values,
                     value=pc.values)
