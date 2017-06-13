"""
The ``tools`` module contains a collection of functions used in the
windpowerlib.

"""

import numpy as np


__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


def smallest_difference(value_1, value_2, comp_value, corresp_1, corresp_2):
    r"""
    Selects the value with the smaller difference to a comparative value.

    Additionally returns a corresponding value. This function is for example
    used in :py:func:`~.modelchain.v_wind_hub` of the
    :class:`~.modelchain.ModelChain` to choose the wind speed data that is
    close to the hub height of the examined wind turbine. In this case
    `value_1` and `value_2` are the heights of the corresponding wind speed
    data sets `corresp_1` and `corresp_2`.

    Parameters
    ----------
    value_1 : float
        First value of which the difference to `comp_value` will be
        compared with the difference to `comp_value` of `value_2`.
    value_2 : float
        Second value for comparison.
    comp_value : float
        Comparative value.
    corresp_1 : pd.Series or np.array or float
        Corresponding value to `value_1`.
    corresp_2 : pd.Series or np.array or float
        Corresponding value to `value_2`.

    Returns
    -------
    Tuple(float, pd.Series or np.array or float)
        Value closer to comparing value as float and its corresponding value as
        float.

    """
    if (value_2 is not None and corresp_2 is not None):
        if abs(value_1 - comp_value) <= abs(value_2 - comp_value):
            closest_value = value_1
        else:
            closest_value = value_2
    else:
        closest_value = value_1

    # Select correponding value
    if closest_value == value_1:
        corresp_value = corresp_1
    else:
        corresp_value = corresp_2
    return (closest_value, corresp_value)


def linear_extra_interpolation(data_frame, requested_height, column_name):
    r"""
    Inter- or extrapolates between the values of a data frame.

    This function can for example be used for the interpolation of a wind
    speed, density or temperature.

    Parameters
    ----------
    data_frame : DataFrame
        Indices are the values between which will be interpolated or from which
        will be extrapolated, the corresponding values are in the column
        specified by `column_name` and they can be floats, pd.Series or
        np.arrays.
    requested_height : float
        Height for which the interpolation takes place (e.g. hub height of wind
        turbine).
    column_name : string
        Name of the column in the DataFrame `data_frame` that contains the
        correponding values.

    Returns
    -------
    interpolant : pandas.Series, numpy.array or float
        Result of the interpolation (e.g. density at hub height).

    Notes
    -----

    For the interpolation np.interp() is used and the following equation is
    used for extrapolation:

    .. math:: interpolant = (value_2 - value_1) / (height_2 - height_1) *
              (requested_height - height_1) + value_1

    with:
        height_2: largest/smallest value in data frame, height_1: second
        largest/smallest value in data frame, value_2: corresponding value to
        height_2, value_1: correponding value to height_1

    """
    if requested_height > max(data_frame.index):
        height_2 = max(data_frame.index)
        value_2 = data_frame[column_name][height_2]
        height_1 = sorted(data_frame.index)[-2]  # Second largest number
        value_1 = data_frame[column_name][height_1]
        interpolant = ((value_2 - value_1) / (height_2 - height_1) *
                       (requested_height - height_1) + value_1)
    elif requested_height < min(data_frame.index):
        height_2 = min(data_frame.index)
        value_2 = data_frame[column_name][height_2]
        height_1 = sorted(data_frame.index)[1]  # Second smallest number
        value_1 = data_frame[column_name][height_1]
        interpolant = ((value_2 - value_1) / (height_2 - height_1) *
                       (requested_height - height_1) + value_1)
    else:
        interpolant = np.interp(requested_height, data_frame.index,
                                data_frame[column_name])
    return interpolant
