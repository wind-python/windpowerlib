"""
The ``tools`` module contains a collection of helper functions used in the
windpowerlib.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import warnings
import pandas as pd


class WindpowerlibUserWarning(UserWarning):
    """
    The WindpowerlibUserWarning is used to warn users if they use the
    windpowerlib in an untypical way. It is not necessarily wrong but could
    lead to an unwanted behaviour if you do not know what you are doing.
    If you know what you are doing you can easily switch the warnings off:

    Examples
    --------
    >>> import warnings
    >>> warnings.filterwarnings("ignore", category=WindpowerlibUserWarning)
    """
    pass


def linear_interpolation_extrapolation(df, target_height):
    r"""
    Linearly inter- or extrapolates between the values of a data frame.

    This function can be used for the linear inter-/extrapolation of a
    parameter (e.g wind speed) available at two or more different heights, to
    approximate the value at hub height.
    The function is carried out when the parameter `wind_speed_model`,
    `density_model` or `temperature_model` of an instance of the
    :class:`~.modelchain.ModelChain` class is 'interpolation_extrapolation'.

    Parameters
    ----------
    df : :pandas:`pandas.DataFrame<frame>`
        DataFrame with time series for parameter that is to be interpolated or
        extrapolated. The columns of the DataFrame are the different heights
        for which the parameter is available. If more than two heights are
        given, the two closest heights are used. See example below on how the
        DataFrame should look like and how the function can be used.
    target_height : float
        Height for which the parameter is approximated (e.g. hub height).

    Returns
    -------
    :pandas:`pandas.Series<series>`
        Result of the inter-/extrapolation (e.g. wind speed at hub height).

    Notes
    -----

    For the inter- and extrapolation the following equation is used:

    .. math:: f(x)=\frac{(f(x_2) - f(x_1))}{(x_2 - x_1)} \cdot
        (x - x_1) + f(x_1)

    Examples
    ---------
    >>> import numpy as np
    >>> import pandas as pd
    >>> wind_speed_10m=np.array([[3], [4]])
    >>> wind_speed_80m=np.array([[6], [6]])
    >>> weather_df=pd.DataFrame(np.hstack((wind_speed_10m,
    ...                                      wind_speed_80m)),
    ...                           index=pd.date_range('1/1/2012',
    ...                                               periods=2,
    ...                                               freq='H'),
    ...                           columns=[np.array(['wind_speed',
    ...                                              'wind_speed']),
    ...                                    np.array([10, 80])])
    >>> value=linear_interpolation_extrapolation(
    ...     weather_df['wind_speed'], 100)[0]

    """
    # find closest heights
    heights_sorted = df.columns[
        sorted(
            range(len(df.columns)),
            key=lambda i: abs(df.columns[i] - target_height),
        )
    ]
    return (df[heights_sorted[1]] - df[heights_sorted[0]]) / (
        heights_sorted[1] - heights_sorted[0]
    ) * (target_height - heights_sorted[0]) + df[heights_sorted[0]]


def logarithmic_interpolation_extrapolation(df, target_height):
    r"""
    Logarithmic inter- or extrapolation between the values of a data frame.

    This function can be used for the logarithmic inter-/extrapolation of the
    wind speed if it is available at two or more different heights, to
    approximate the value at hub height.
    The function is carried out when the parameter `wind_speed_model`
    :class:`~.modelchain.ModelChain` class is
    'log_interpolation_extrapolation'.

    Parameters
    ----------
    df : :pandas:`pandas.DataFrame<frame>`
        DataFrame with time series for parameter that is to be interpolated or
        extrapolated. The columns of the DataFrame are the different heights
        for which the parameter is available. If more than two heights are
        given, the two closest heights are used. See example in
        :py:func:`~.linear_interpolation_extrapolation` on how the
        DataFrame should look like and how the function can be used.
    target_height : float
        Height for which the parameter is approximated (e.g. hub height).

    Returns
    -------
    :pandas:`pandas.Series<series>`
        Result of the inter-/extrapolation (e.g. wind speed at hub height).

    Notes
    -----

    For the logarithmic inter- and extrapolation the following equation is
    used [1]_:

    .. math:: f(x)=\frac{\ln(x) \cdot (f(x_2) - f(x_1)) - f(x_2) \cdot
        \ln(x_1) + f(x_1) \cdot \ln(x_2)}{\ln(x_2) - \ln(x_1)}

    References
    ----------
    .. [1] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 83

    """
    # find closest heights
    heights_sorted = df.columns[
        sorted(
            range(len(df.columns)),
            key=lambda i: abs(df.columns[i] - target_height),
        )
    ]
    return (
        np.log(target_height) * (df[heights_sorted[1]] - df[heights_sorted[0]])
        - df[heights_sorted[1]] * np.log(heights_sorted[0])
        + df[heights_sorted[0]] * np.log(heights_sorted[1])
    ) / (np.log(heights_sorted[1]) - np.log(heights_sorted[0]))


def gauss_distribution(function_variable, standard_deviation, mean=0):
    r"""
    Gauss distribution.

    The Gauss distribution is used in the function
    :py:func:`~.power_curves.smooth_power_curve` for power curve smoothing.

    Parameters
    ----------
    function_variable : float
        Variable of the gaussian distribution.
    standard_deviation : float
        Standard deviation of the Gauss distribution.
    mean : float
        Defines the offset of the Gauss distribution. Default: 0.

    Returns
    -------
    :pandas:`pandas.Series<series>` or numpy.array
        Wind speed at hub height. Data type depends on the type of
        `wind_speed`.

    Notes
    -----
    The following equation is used [1]_:

    .. math:: f(x)=\frac{1}{\sigma \sqrt{2 \pi}} \exp
                     \left[-\frac{(x-\mu)^2}{2 \sigma^2}\right]

    with:
        :math:`\sigma`: standard deviation, :math:`\mu`: mean

    References
    ----------
    .. [1] Berendsen, H.: "A Student's Guide to Data and Error Analysis".
             New York, Cambridge University Press, 2011, p. 37

    """
    return (1 / (standard_deviation * np.sqrt(2 * np.pi)) *
            np.exp(-(function_variable - mean)**2 /
                   (2 * standard_deviation**2)))


def estimate_turbulence_intensity(height, roughness_length):
    r"""
    Estimate turbulence intensity by the roughness length.

    Parameters
    ----------
    height : float
        Height above ground in m at which the turbulence intensity is
        calculated.
    roughness_length : pandas.Series or numpy.array or float
        Roughness length.

    Notes
    -----
    The following equation is used [1]_:

    .. math:: TI=\frac{1}{\ln\left(\frac{h}{z_\text{0}}\right)}

    with:
        TI: turbulence intensity, h: height, :math:`z_{0}`: roughness length

    References
    ----------
    .. [1] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 88

    """
    return 1 / (np.log(height / roughness_length))


def check_weather_data(weather_df):
    """
    Check weather Data Frame.

    - Raise warning if there are nan values.
    - Convert columns if heights are string and not numeric.

    """
    # Convert data heights to integer. In some case they are strings.
    weather_df.columns = pd.MultiIndex.from_arrays(
        [
            weather_df.columns.get_level_values(0),
            pd.to_numeric(weather_df.columns.get_level_values(1)),
        ]
    )

    # check for nan values
    if weather_df.isnull().any().any():
        nan_columns = list(weather_df.columns[weather_df.isnull().any()])
        msg = (
            "The following columns of the weather data contain invalid "
            "values like 'nan': {0}"
        )
        warnings.warn(msg.format(nan_columns), WindpowerlibUserWarning)
    return weather_df
