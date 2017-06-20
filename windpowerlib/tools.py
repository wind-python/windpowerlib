"""
The ``tools`` module contains a collection of functions used in the
windpowerlib.

"""


__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"


def smallest_difference(data_frame, comp_value, column_name):
    r"""
    Selects a value with the smallest difference to a comparative value.

    Additionally returns a corresponding value. This function is for example
    used in :py:func:`~.modelchain.v_wind_hub` of the
    :class:`~.modelchain.ModelChain` to choose the wind speed data that is the
    closest to the hub height of the examined wind turbine. In this case the
    column of the data frame contains wind speed time series and the indices
    are the corresponding heights for which these time series apply.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Indices are the values of which the smallest difference to `comp_value`
        will be found, the corresponding values are in the column
        specified by `column_name` and they can be floats, pandas.Series or
        numpy.arrays.
    comp_value : float
        Comparative value.
    column_name : string
        Name of the column in the `data_frame` that contains the
        corresponding values.

    Returns
    -------
    Tuple(float, float or pandas.Series or numpy.array)
        Closest value to comparative value as float and its corresponding value
        as float, pandas.Series or numpy.array.

    """
    # Calculate difference to comp_value for all indices of data_frame
    diff = []
    for index in sorted(data_frame.index):
        diff.append(abs(comp_value - index))
    # Find smallest difference
    closest_value = sorted(data_frame.index)[diff.index(min(diff))]
    corresp_value = data_frame[column_name][closest_value]
    return closest_value, corresp_value


def linear_extra_interpolation(data_frame, requested_height, column_name):
    r"""
    Inter- or extrapolates between the values of a data frame.

    This function can for example be used for the interpolation of a wind
    speed, density or temperature to calculated these values at hub height of a
    wind turbine.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        Indices are the values between which will be interpolated or from which
        will be extrapolated, the corresponding values are in the column
        specified by `column_name` and can be floats, pandas.Series or
        numpy.arrays.
    requested_height : float
        Height for which the interpolation takes place (e.g. hub height of wind
        turbine).
    column_name : string
        Name of the column in the DataFrame `data_frame` that contains the
        corresponding values.

    Returns
    -------
    interpolant : float or pandas.Series or numpy.array
        Result of the interpolation (e.g. density at hub height).

    Notes
    -----

    For the inter- and extrapolation the following equation is used:

    .. math:: interpolant = (value_2 - value_1) / (height_2 - height_1) *
              (height_{requested} - height_1) + value_1

    with:
        :math:`height_2`: index of data frame closest to
        :math:`height_{requested}`, :math:`height_1`: index of data frame
        second closest to :math:`height_{requested}`,
        :math:`value_2`: corresponding value to `height_2`,
        :math:`value_1`: corresponding value to `height_1`,
        :math:`height_{requested}` : height for which the interpolation takes
        place

    """
    # Get closest index of data_frame to requested_height
    height_2, value_2 = smallest_difference(data_frame, requested_height,
                                            column_name)
    # Drop row with closest index to requested_height and get second closest
    data_frame_2 = data_frame.drop(height_2)
    height_1, value_1 = smallest_difference(data_frame_2, requested_height,
                                            column_name)
    # Interpolation
    interpolant = ((value_2 - value_1) / (height_2 - height_1) *
                   (requested_height - height_1) + value_1)
    return interpolant
