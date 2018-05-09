"""
The ``wake_losses`` module contains functions for modelling wake losses by wind
efficiency curves (reduction of wind speed).

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
import pandas as pd
import os

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None


def reduce_wind_speed(wind_speed, wind_efficiency_curve_name='dena_mean'):
    """
    Reduces wind speed by a wind efficiency curve.

    The wind efficiency curves are provided in the windpowerlib and were
    calculated in the dena-Netzstudie II and in the work of Knorr
    (see [1]_ and [2]_).

    Parameters
    ----------
    wind_speed : pandas.Series or numpy.array
        Wind speed time series.
    wind_efficiency_curve_name : string
        Name of the wind efficiency curve. Use display_wind_efficiency_curves()
        to see all provided wind efficiency curves.

    Returns
    -------
    reduced_wind_speed : pd.Series or np.array
        `wind_speed` reduced by wind efficiency curve.

    References
    ----------
    .. [1] Kohler et.al.: "dena-Netzstudie II. Integration erneuerbarer
            Energien in die deutsche Stromversorgung im Zeitraum 2015 – 2020
            mit Ausblick 2025.", Deutsche Energie-Agentur GmbH (dena),
            Tech. rept., 2010, p. 101
    .. [2] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 124

    """
    # Get wind efficiency curve
    wind_efficiency_curve = get_wind_efficiency_curve(
        curve_name=wind_efficiency_curve_name)
    # Reduce wind speed by wind efficiency
    reduced_wind_speed = wind_speed * np.interp(
        wind_speed, wind_efficiency_curve['wind_speed'],
        wind_efficiency_curve['efficiency'])
    return reduced_wind_speed


def get_wind_efficiency_curve(curve_name='dena_mean'):
    r"""
    Reads wind efficiency curve specified in `curve_name`.

    Parameters
    ----------
    curve_name : String
        Specifies the curve. Use display_wind_efficiency_curves() to see all
        provided wind efficiency curves. Default: 'dena_mean'.

    Returns
    -------
    efficiency_curve : pd.DataFrame
        Wind efficiency curve. Contains 'wind_speed' and 'efficiency' columns
        with wind speed in m/s and wind efficiency (dimensionless).

    Notes
    -----
    The wind efficiency curves were generated in the "Dena Netzstudie" and in
    the disseration of Kaspar Knorr. For more information see [1]_ and [2]_.

    References
    ----------
    .. [1] Kohler et.al.: "dena-Netzstudie II. Integration erneuerbarer
            Energien in die deutsche Stromversorgung im Zeitraum 2015 – 2020
            mit Ausblick 2025.", Deutsche Energie-Agentur GmbH (dena),
            Tech. rept., 2010, p. 101
    .. [2] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 124

    """
    possible_curve_names = ['dena_mean', 'knorr_mean', 'dena_extreme1',
                            'dena_extreme2', 'knorr_extreme1',
                            'knorr_extreme2', 'knorr_extreme3']
    if curve_name.split('_')[0] not in ['dena', 'knorr']:
        raise ValueError("`curve_name` must be one of the following: " +
                         "{} but is {}".format(possible_curve_names,
                                               curve_name))
    path = os.path.join(os.path.dirname(__file__), 'data',
                        'wind_efficiency_curves_{}.csv'.format(
                            curve_name.split('_')[0]))
    # Read wind efficiency curves from file
    wind_efficiency_curves = pd.read_csv(path)
    # Raise error if wind efficiency curve specified in 'curve_name' does not
    # exist
    if curve_name not in list(wind_efficiency_curves):
        raise ValueError("Efficiency curve name does not exist. Must be one" +
                         "of the following: {}".format(possible_curve_names) +
                         "but is {}".format(curve_name))
    # Get wind efficiency curve and rename column containing efficiency
    efficiency_curve = wind_efficiency_curves[['wind_speed', curve_name]]
    efficiency_curve.columns = ['wind_speed', 'efficiency']
    return efficiency_curve


def display_wind_efficiency_curves():
    r"""
    Displays all wind efficiency curves available in the windpowerlib.

    Notes
    -----
    The wind efficiency curves were generated in the "Dena Netzstudie" and in
    the disseration of Kaspar Knorr. For more information see [1]_ and [2]_.

    References
    ----------
    .. [1] Kohler et.al.: "dena-Netzstudie II. Integration erneuerbarer
            Energien in die deutsche Stromversorgung im Zeitraum 2015 – 2020
            mit Ausblick 2025.", Deutsche Energie-Agentur GmbH (dena),
            Tech. rept., 2010, p. 101
    .. [2] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 124

    """
    origins = ['dena', 'knorr']
    paths = [os.path.join(os.path.dirname(__file__), 'data',
                          'wind_efficiency_curves_{}.csv'.format(origin)) for
             origin in origins]
    # Read wind efficiency curves from files
    # Create separate data frames for origin of curve
    dena_df = pd.read_csv(paths[0])
    knorr_df = pd.read_csv(paths[1])
    # Print names of all available curves
    curves_list = [col for col in dena_df if 'wind_speed' not in col]
    curves_list.extend([col for col in knorr_df if 'wind_speed' not in col])
    print("Names of the provided wind efficiency curves are the " +
          "following: {}".format(curves_list))
    if plt:
        # Create data frames for plot
        dena_df.set_index('wind_speed', inplace=True)
        knorr_df.set_index('wind_speed', inplace=True)
        fig, ax = plt.subplots()
        dena_df.plot(ax=ax, legend=True)
        knorr_df.plot(ax=ax, legend=True)
        plt.ylabel('Wind farm efficiency')
        plt.xlabel('Wind speed m/s')
        plt.show()
    else:
        print(dena_df)
        print(knorr_df)

if __name__ == "__main__":
    display_wind_efficiency_curves()
